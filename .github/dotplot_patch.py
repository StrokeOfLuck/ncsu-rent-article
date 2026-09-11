from pathlib import Path

p = Path("index.html")
s = p.read_text(encoding="utf-8")

old = '''.housing-rate-row::after{
  content:"";
  grid-column:2;
  grid-row:1;
  justify-self:start;
  align-self:stretch;
  width:2px;
  margin-left:42.5%;
  margin-bottom:-8px;
  background:#6fb4f2;
  opacity:.9;
  z-index:0;
  pointer-events:none;
}
.housing-rate-row:last-child::after{
  margin-bottom:0;
}
.housing-rate-label,
.housing-rate-value,
.housing-rate-plot{
  position:relative;
  z-index:1;
}'''
new = '''.housing-rate-plot::after{
  content:"";
  position:absolute;
  left:42.5%;
  top:-13px;
  bottom:-13px;
  border-left:2px solid #6fb4f2;
  opacity:.9;
  z-index:0;
  pointer-events:none;
}
.housing-rate-dot{
  z-index:2;
}'''
if old in s:
    s = s.replace(old, new)
elif '.housing-rate-plot::after{' not in s:
    raise SystemExit("Could not find current CPI row-line CSS")

mobile = '''
@media(max-width:700px){
  .housing-rate-row::after{
    grid-column:1 / -1;
    grid-row:1 / 3;
    margin-left:42.5%;
  }
}
'''
s = s.replace(mobile, '\n')

# Keep the axis benchmark strong but do not let it extend so far that it distorts spacing.
s = s.replace('''  top:13px;\n  height:35px;\n  border-left:2px solid #6fb4f2;''', '''  top:13px;\n  height:27px;\n  border-left:2px solid #6fb4f2;''')

# The percentage labels already define the scale, so the extra horizontal axis baseline only adds visual clutter.
s = s.replace(''' .housing-rate-axis-plot{'''.lstrip() + '''
  position:relative;
  height:32px;
  border-bottom:1px solid var(--line);
}''', '''.housing-rate-axis-plot{
  position:relative;
  height:32px;
}''')

p.write_text(s, encoding="utf-8")
