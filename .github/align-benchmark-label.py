from pathlib import Path

p = Path("index.html")
s = p.read_text(encoding="utf-8")

marker = "/* Compact BLS benchmark axis */"
if marker not in s:
    css = r'''

/* Compact BLS benchmark axis */
.housing-rate-chart{
  padding-top:4px;
}
.housing-rate-axis{
  margin-bottom:7px;
}
.housing-rate-axis-plot{
  height:8px;
}
.housing-rate-active-label::after{
  top:calc(100% + 1px);
  height:20px;
}
/* End compact BLS benchmark axis */
'''
    if '</style>' not in s:
        raise SystemExit("Could not find closing style tag")
    s = s.replace('</style>', css + '\n</style>', 1)

p.write_text(s, encoding="utf-8")
