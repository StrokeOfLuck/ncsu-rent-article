from pathlib import Path
import re

p = Path("index.html")
s = p.read_text(encoding="utf-8")

chart_start = s.find('<div class="housing-rate-chart"')
context_start = s.find('<div class="housing-rate-context">', chart_start)
if chart_start == -1 or context_start == -1:
    raise SystemExit("Could not find housing-rate chart block")

chart = s[chart_start:context_start]

dollar_changes = {
    "Doubles": 170,
    "Singles": 325,
    "Wolf Village/Wolf Ridge — 1 bedroom/studio": 375,
    "Wolf Village/Wolf Ridge — 2, 3 or 4 bedrooms": 280,
    "E.S. King — 1-bedroom undergraduate double": 225,
    "E.S. King/Western Manor — studio": 250,
    "E.S. King/Western Manor — 1 bedroom": 225,
    "E.S. King/Western Manor — 2 bedroom": 300,
    "Coastal Quarters — single": 125,
    "Coastal Quarters — double": 75,
}

rows = re.findall(r'\n\s*(<div class="housing-rate-row">.*?</div></div>)', chart)
if len(rows) != 10:
    raise SystemExit(f"Expected 10 housing rows, found {len(rows)}")

for row in rows:
    label_match = re.search(r'<strong>(.*?)</strong>', row)
    if not label_match:
        raise SystemExit("A housing row is missing its label")
    label = label_match.group(1)
    if label not in dollar_changes:
        raise SystemExit(f"Unexpected housing row label: {label}")

    amount = dollar_changes[label]
    updated_row = row

    # Desktop: a dedicated dollar-change column between the housing label and plot.
    if 'class="housing-rate-dollar"' not in updated_row:
        plot_token = '<div class="housing-rate-plot">'
        if plot_token not in updated_row:
            raise SystemExit(f"Could not find dot plot in row: {label}")
        replacement = (
            f'<div class="housing-rate-dollar" aria-label="Dollar increase">+${amount:,}</div>'
            + plot_token
        )
        updated_row = updated_row.replace(plot_token, replacement, 1)

    # Mobile: keep the chart compact by putting the dollar increase directly on
    # the existing price line instead of adding another grid column or row.
    if 'class="housing-rate-mobile-dollar"' not in updated_row:
        label_pattern = re.compile(r'(<div class="housing-rate-label">.*?)(</div>)', re.S)
        updated_row, count = label_pattern.subn(
            rf'\1 <span class="housing-rate-mobile-dollar">(+$' + f'{amount:,}' + r')</span>\2',
            updated_row,
            count=1,
        )
        if count != 1:
            raise SystemExit(f"Could not add mobile dollar increase to row: {label}")

    chart = chart.replace(row, updated_row, 1)

# Add the heading over the desktop dollar-change column.
if 'class="housing-rate-dollar-heading"' not in chart:
    axis_pattern = re.compile(
        r'(<div class="housing-rate-type-heading">Housing Type/Location</div>\s*)'
        r'(<div class="housing-rate-axis-plot">)'
    )
    chart, count = axis_pattern.subn(
        r'\1<div class="housing-rate-dollar-heading">Dollar increase</div>\n          \2',
        chart,
        count=1,
    )
    if count != 1:
        raise SystemExit("Could not add dollar-increase axis heading")

s = s[:chart_start] + chart + s[context_start:]

marker = "/* Housing-rate dollar increase */"
css = r'''

/* Housing-rate dollar increase */
.housing-rate-dollar-heading,
.housing-rate-dollar,
.housing-rate-mobile-dollar{
  display:none;
}

@media(min-width:901px){
  .housing-rate-axis,
  .housing-rate-row{
    grid-template-columns:minmax(330px,1.2fr) 94px minmax(280px,1fr) 58px !important;
    column-gap:12px !important;
  }

  .housing-rate-dollar-heading{
    display:block;
    align-self:end;
    padding-bottom:1px;
    color:var(--muted);
    font-size:8.5px;
    font-weight:800;
    text-align:center;
    white-space:nowrap;
  }

  .housing-rate-dollar{
    display:block;
    color:var(--ink);
    font-size:10.5px;
    font-weight:800;
    text-align:center;
    white-space:nowrap;
    font-variant-numeric:tabular-nums;
  }
}

@media(max-width:700px){
  .housing-rate-mobile-dollar{
    display:inline;
    margin-left:2px;
    color:var(--muted);
    font-size:.9em;
    font-weight:750;
    white-space:nowrap;
    font-variant-numeric:tabular-nums;
  }
}
/* End housing-rate dollar increase */
'''

# Replace either the earlier desktop-only block or this newer combined block.
css_pattern = re.compile(
    r'/\* (?:Desktop housing-rate dollar increase column|Housing-rate dollar increase) \*/.*?'
    r'/\* End (?:desktop housing-rate dollar increase column|housing-rate dollar increase) \*/',
    re.S | re.I,
)
if css_pattern.search(s):
    s = css_pattern.sub(css.strip(), s, count=1)
else:
    if '</style>' not in s:
        raise SystemExit("Could not find closing style tag")
    s = s.replace('</style>', css + '\n</style>', 1)

p.write_text(s, encoding="utf-8")
