from pathlib import Path

p = Path("index.html")
s = p.read_text(encoding="utf-8")

old_axis = '''.housing-rate-cpi-label::after{
  content:"";
  position:absolute;
  left:50%;
  top:13px;
  height:19px;
  border-left:2px solid #6fb4f2;
  opacity:1;
}'''
new_axis = '''.housing-rate-cpi-label::after{
  content:"";
  position:absolute;
  left:50%;
  top:13px;
  height:35px;
  border-left:2px solid #6fb4f2;
  opacity:1;
}'''
if old_axis in s:
    s = s.replace(old_axis, new_axis)
elif new_axis not in s:
    raise SystemExit("Could not find CPI axis line CSS")

old_segments = '''.housing-rate-plot::after{
  content:"";
  position:absolute;
  left:42.5%;
  top:-5px;
  bottom:-5px;
  border-left:2px solid #6fb4f2;
  opacity:.9;
}'''
new_continuous = '''.housing-rate-row::after{
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
if old_segments in s:
    s = s.replace(old_segments, new_continuous)
elif '.housing-rate-row::after{' not in s:
    raise SystemExit("Could not find segmented CPI line CSS")

mobile = '''
@media(max-width:700px){
  .housing-rate-row::after{
    grid-column:1 / -1;
    grid-row:1 / 3;
    margin-left:42.5%;
  }
}
'''
if mobile.strip() not in s:
    marker = '/* End housing rate dot plot */'
    if marker not in s:
        raise SystemExit("Could not find dot plot CSS end marker")
    s = s.replace(marker, mobile + marker, 1)

p.write_text(s, encoding="utf-8")
