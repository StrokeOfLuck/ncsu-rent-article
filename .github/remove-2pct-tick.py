from pathlib import Path

p = Path("index.html")
s = p.read_text(encoding="utf-8")
old = '            <span class="housing-rate-axis-tick" style="left:25%">2%</span>\n'
if old not in s:
    raise SystemExit("2% housing-rate axis tick not found")
s = s.replace(old, "", 1)
p.write_text(s, encoding="utf-8")
