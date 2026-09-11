from pathlib import Path

p = Path("index.html")
s = p.read_text(encoding="utf-8")

compact_marker = "/* Compact BLS benchmark axis */"
if compact_marker not in s:
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

line_marker = "/* Keep BLS benchmark line below label */"
if line_marker not in s:
    css = r'''

/* Keep BLS benchmark line below label */
.housing-rate-active-label{
  background:var(--paper);
  padding:0 3px;
}
.housing-rate-active-label::after{
  top:calc(100% + 3px) !important;
  height:12px !important;
}
.housing-rate-axis + .housing-rate-row .housing-rate-benchmark-line{
  top:0 !important;
}
/* End keep BLS benchmark line below label */
'''
    if '</style>' not in s:
        raise SystemExit("Could not find closing style tag")
    s = s.replace('</style>', css + '\n</style>', 1)

p.write_text(s, encoding="utf-8")
