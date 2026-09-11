from pathlib import Path

p = Path("index.html")
s = p.read_text(encoding="utf-8")

changes = [
    (
        '<span class="housing-rate-cpi-label">CPI 3.4%</span>',
        '<span class="housing-rate-cpi-label">Overall CPI 3.4%</span>',
    ),
    (
        'A vertical reference line marks U.S. CPI inflation at 3.4 percent.',
        'A vertical reference line marks overall U.S. CPI inflation at 3.4 percent.',
    ),
    (
        '''.housing-rate-cpi-label{\n  position:absolute;\n  left:42.5%;\n  top:0;\n  transform:translateX(-50%);\n  color:var(--blue);\n  font-size:8.5px;\n  font-weight:800;\n  white-space:nowrap;\n}''',
        '''.housing-rate-cpi-label{\n  position:absolute;\n  left:42.5%;\n  top:0;\n  transform:translateX(-50%);\n  color:#6fb4f2;\n  font-size:8.5px;\n  font-weight:900;\n  white-space:nowrap;\n}''',
    ),
    (
        '''.housing-rate-cpi-label::after{\n  content:"";\n  position:absolute;\n  left:50%;\n  top:13px;\n  height:19px;\n  border-left:1px dashed var(--blue);\n  opacity:.7;\n}''',
        '''.housing-rate-cpi-label::after{\n  content:"";\n  position:absolute;\n  left:50%;\n  top:13px;\n  height:19px;\n  border-left:2px solid #6fb4f2;\n  opacity:1;\n}''',
    ),
    (
        '''.housing-rate-plot::after{\n  content:"";\n  position:absolute;\n  left:42.5%;\n  top:-5px;\n  bottom:-5px;\n  border-left:1px dashed var(--blue);\n  opacity:.55;\n}''',
        '''.housing-rate-plot::after{\n  content:"";\n  position:absolute;\n  left:42.5%;\n  top:-5px;\n  bottom:-5px;\n  border-left:2px solid #6fb4f2;\n  opacity:.9;\n}''',
    ),
]

for old, new in changes:
    if old in s:
        s = s.replace(old, new)
    elif new not in s:
        raise SystemExit(f"Could not find expected CPI chart text/CSS:\n{old[:120]}")

p.write_text(s, encoding="utf-8")
