from pathlib import Path
import re

p = Path("index.html")
s = p.read_text(encoding="utf-8")

# Add the same left-column heading NC State uses.
axis = '<div class="housing-rate-axis" aria-hidden="true">\n          <div></div>'
axis_new = '<div class="housing-rate-axis" aria-hidden="true">\n          <div class="housing-rate-type-heading">Housing Type/Location</div>'
if axis in s:
    s = s.replace(axis, axis_new, 1)

# Put the housing rows in the same sequence and wording as NC State's source table.
chart_start = s.find('<div class="housing-rate-chart"')
context_start = s.find('<div class="housing-rate-context">', chart_start)
if chart_start == -1 or context_start == -1:
    raise SystemExit("Could not find housing-rate chart block")

chart = s[chart_start:context_start]
chart = chart.replace('<strong>Double</strong>', '<strong>Doubles</strong>', 1)
chart = chart.replace('<strong>Single</strong>', '<strong>Singles</strong>', 1)

rows = re.findall(r'\n\s*(<div class="housing-rate-row">.*?</div></div>)', chart)
if len(rows) != 10:
    raise SystemExit(f"Expected 10 housing rows, found {len(rows)}")

order = [
    'Doubles',
    'Singles',
    'Wolf Village/Wolf Ridge — 1 bedroom/studio',
    'Wolf Village/Wolf Ridge — 2, 3 or 4 bedrooms',
    'E.S. King — 1-bedroom undergraduate double',
    'E.S. King/Western Manor — studio',
    'E.S. King/Western Manor — 1 bedroom',
    'E.S. King/Western Manor — 2 bedroom',
    'Coastal Quarters — single',
    'Coastal Quarters — double',
]

by_label = {}
for row in rows:
    m = re.search(r'<strong>(.*?)</strong>', row)
    if not m:
        raise SystemExit("A housing row is missing its label")
    by_label[m.group(1)] = row

missing = [label for label in order if label not in by_label]
if missing:
    raise SystemExit(f"Missing housing rows: {missing}")

first_row_pos = min(chart.find(row) for row in rows)
last_row_end = max(chart.find(row) + len(row) for row in rows)
ordered_rows = '\n        ' + '\n        '.join(by_label[label] for label in order) + '\n      '
chart = chart[:first_row_pos] + ordered_rows + chart[last_row_end:]
s = s[:chart_start] + chart + s[context_start:]

marker = "/* Housing rate source-order heading */"
if marker not in s:
    css = r'''

/* Housing rate source-order heading */
.housing-rate-type-heading{
  color:var(--muted);
  font-size:8.5px;
  font-weight:800;
  white-space:nowrap;
  align-self:end;
  padding-bottom:1px;
}
@media(max-width:700px){
  .housing-rate-type-heading{
    display:none;
  }
}
/* End housing rate source-order heading */
'''
    if '</style>' not in s:
        raise SystemExit("Could not find closing style tag")
    s = s.replace('</style>', css + '\n</style>', 1)

baseline_marker = "/* Align BLS benchmark label baseline with axis ticks */"
if baseline_marker not in s:
    css = r'''

/* Align BLS benchmark label baseline with axis ticks */
.housing-rate-axis-tick,
.housing-rate-active-label{
  bottom:-15px !important;
  line-height:1 !important;
}
/* End align BLS benchmark label baseline with axis ticks */
'''
    if '</style>' not in s:
        raise SystemExit("Could not find closing style tag")
    s = s.replace('</style>', css + '\n</style>', 1)

mobile_marker = "/* Mobile housing-rate chart cleanup */"
if mobile_marker not in s:
    css = r'''

/* Mobile housing-rate chart cleanup */
@media(max-width:700px){
  .housing-rate-chart{
    padding-top:2px;
  }

  .housing-rate-axis{
    grid-template-columns:1fr !important;
    margin-bottom:4px !important;
  }

  .housing-rate-axis-plot{
    grid-column:1 !important;
    height:22px !important;
  }

  .housing-rate-row{
    grid-template-columns:minmax(0,1fr) 54px !important;
    grid-template-rows:auto 22px !important;
    column-gap:10px !important;
    row-gap:5px !important;
    align-items:start !important;
    padding:8px 0 3px;
  }

  .housing-rate-label{
    grid-column:1 !important;
    grid-row:1 !important;
    min-width:0;
    padding-right:2px;
    font-size:8.8px !important;
    line-height:1.22 !important;
  }

  .housing-rate-label strong{
    font-size:9.7px !important;
    line-height:1.22 !important;
    white-space:normal;
    overflow-wrap:anywhere;
  }

  .housing-rate-value{
    grid-column:2 !important;
    grid-row:1 !important;
    align-self:start !important;
    padding-top:0 !important;
    text-align:right;
    white-space:nowrap;
  }

  .housing-rate-plot{
    grid-column:1 / -1 !important;
    grid-row:2 !important;
    height:22px !important;
    margin-top:0 !important;
  }

  .housing-rate-plot .housing-rate-benchmark-line{
    top:0 !important;
    bottom:0 !important;
    height:auto !important;
  }

  .housing-rate-axis + .housing-rate-row .housing-rate-benchmark-line{
    top:0 !important;
    bottom:0 !important;
  }

  .housing-rate-context{
    grid-template-columns:repeat(2,minmax(0,1fr)) !important;
    gap:0 !important;
  }

  .housing-rate-context-title,
  .housing-rate-context-note{
    grid-column:1 / -1 !important;
  }

  .housing-rate-context > .housing-rate-context-item{
    min-width:0;
  }
}
/* End mobile housing-rate chart cleanup */
'''
    if '</style>' not in s:
        raise SystemExit("Could not find closing style tag")
    s = s.replace('</style>', css + '\n</style>', 1)

p.write_text(s, encoding="utf-8")
