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

# Split the active benchmark into a name and percentage. Desktop keeps them inline;
# mobile stacks the name above the percentage and centers both on the reference line.
plain_label = '<span id="housing-rate-active-label" class="housing-rate-active-label" style="left:37.5%">Lodging while at school 3.0%</span>'
split_label = '<span id="housing-rate-active-label" class="housing-rate-active-label" style="left:37.5%"><span class="housing-rate-active-name">Lodging while at school</span><span class="housing-rate-active-pct">3.0%</span></span>'
if plain_label in s:
    s = s.replace(plain_label, split_label, 1)

old_benchmarks = """  const benchmarks = {
    school: { label: 'Lodging while at school 3.0%', left: '37.5%' },
    rent:   { label: 'Rent of primary residence 2.9%', left: '36.25%' },
    cpi:    { label: 'All items CPI 3.4%', left: '42.5%' }
  };"""
new_benchmarks = """  const benchmarks = {
    school: { name: 'Lodging while at school', pct: '3.0%', left: '37.5%' },
    rent:   { name: 'Rent of primary residence', pct: '2.9%', left: '36.25%' },
    cpi:    { name: 'All items CPI', pct: '3.4%', left: '42.5%' }
  };"""
if old_benchmarks in s:
    s = s.replace(old_benchmarks, new_benchmarks, 1)

old_label_js = "    label.textContent = benchmark.label;"
new_label_js = "    label.innerHTML = `<span class=\"housing-rate-active-name\">${benchmark.name}</span><span class=\"housing-rate-active-pct\">${benchmark.pct}</span>`;"
if old_label_js in s:
    s = s.replace(old_label_js, new_label_js, 1)

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

split_marker = "/* Split active BLS benchmark label */"
if split_marker not in s:
    css = r'''

/* Split active BLS benchmark label */
.housing-rate-active-name,
.housing-rate-active-pct{
  display:inline;
}
.housing-rate-active-pct{
  margin-left:3px;
}
/* End split active BLS benchmark label */
'''
    if '</style>' not in s:
        raise SystemExit("Could not find closing style tag")
    s = s.replace('</style>', css + '\n</style>', 1)

mobile_css = r'''
/* Mobile housing-rate chart cleanup */
@media(max-width:700px){
  .housing-rate-chart{
    padding-top:2px;
  }

  /* Keep the dot plot in its own right-side column on mobile. */
  .housing-rate-axis,
  .housing-rate-row{
    grid-template-columns:minmax(118px,.9fr) minmax(130px,1.1fr) 46px !important;
    column-gap:7px !important;
    align-items:center !important;
  }

  .housing-rate-axis{
    margin-bottom:7px !important;
  }

  .housing-rate-axis > div:first-child,
  .housing-rate-axis > div:last-child{
    display:block !important;
  }

  .housing-rate-axis-plot{
    grid-column:2 !important;
    height:30px !important;
  }

  .housing-rate-row{
    grid-template-rows:auto !important;
    row-gap:0 !important;
    padding:8px 0 !important;
  }

  .housing-rate-label{
    grid-column:1 !important;
    grid-row:1 !important;
    min-width:0;
    padding-right:0;
    font-size:8.5px !important;
    line-height:1.2 !important;
  }

  .housing-rate-label strong{
    font-size:9.4px !important;
    line-height:1.18 !important;
    white-space:normal;
    overflow-wrap:anywhere;
  }

  .housing-rate-plot{
    grid-column:2 !important;
    grid-row:1 !important;
    height:22px !important;
    margin:0 !important;
  }

  .housing-rate-value{
    grid-column:3 !important;
    grid-row:1 !important;
    align-self:center !important;
    padding-top:0 !important;
    text-align:right;
    white-space:nowrap;
    font-size:10px !important;
  }

  /* Name centered above the percentage; percentage centered on the line. */
  .housing-rate-active-label{
    bottom:-15px !important;
    display:flex !important;
    flex-direction:column !important;
    align-items:center !important;
    justify-content:flex-end !important;
    gap:1px !important;
    text-align:center !important;
    line-height:1 !important;
    white-space:nowrap !important;
    font-size:7.1px !important;
  }

  .housing-rate-active-name{
    display:block !important;
    margin:0 !important;
    text-align:center !important;
  }

  .housing-rate-active-pct{
    display:block !important;
    margin:0 !important;
    font-size:8.2px !important;
    font-weight:900 !important;
    text-align:center !important;
  }

  .housing-rate-active-label::after{
    top:calc(100% + 3px) !important;
    height:22px !important;
    border-left:2px solid #6fb4f2 !important;
    border-left-style:solid !important;
  }

  /* Keep the mobile benchmark line solid and visually continuous. */
  .housing-rate-plot .housing-rate-benchmark-line{
    top:-10px !important;
    bottom:-10px !important;
    height:auto !important;
    border-left:2px solid #6fb4f2 !important;
    border-left-style:solid !important;
    opacity:.95 !important;
  }

  .housing-rate-axis + .housing-rate-row .housing-rate-benchmark-line{
    top:-10px !important;
  }

  /* Return the benchmark cards to a simple vertical stack on phones. */
  .housing-rate-context{
    grid-template-columns:1fr !important;
    gap:0 !important;
  }

  .housing-rate-context-title{
    order:0;
    grid-column:1 !important;
  }

  /* Mobile order: school, rent, CPI, minimum wage. */
  .housing-rate-context > .housing-rate-context-item:nth-child(3){ order:1; }
  .housing-rate-context > .housing-rate-context-item:nth-child(4){ order:2; }
  .housing-rate-context > .housing-rate-context-item:nth-child(5){ order:3; }
  .housing-rate-context > .housing-rate-context-item:nth-child(2){ order:4; }

  .housing-rate-context-note{
    order:5;
    grid-column:1 !important;
  }

  .housing-rate-context > .housing-rate-context-item,
  .housing-rate-context > .housing-rate-context-item:nth-child(2),
  .housing-rate-context > .housing-rate-context-item:nth-child(3),
  .housing-rate-context > .housing-rate-context-item:nth-child(4),
  .housing-rate-context > .housing-rate-context-item:nth-child(5){
    padding:9px 0 !important;
    border-left:0 !important;
    border-top:1px solid var(--line) !important;
    min-width:0;
  }
}
/* End mobile housing-rate chart cleanup */
'''

mobile_pattern = re.compile(
    r'/\* Mobile housing-rate chart cleanup \*/.*?/\* End mobile housing-rate chart cleanup \*/',
    re.S,
)
if mobile_pattern.search(s):
    s = mobile_pattern.sub(mobile_css.strip(), s, count=1)
else:
    if '</style>' not in s:
        raise SystemExit("Could not find closing style tag")
    s = s.replace('</style>', '\n' + mobile_css + '\n</style>', 1)

p.write_text(s, encoding="utf-8")
