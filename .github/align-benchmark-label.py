from pathlib import Path
import re

p = Path("index.html")
s = p.read_text(encoding="utf-8")

pattern = r'(\.housing-rate-active-label\{\s*position:absolute;\s*)top:0;'
s2, n = re.subn(pattern, r'\1bottom:-15px;', s, count=1)

if n != 1:
    raise SystemExit(f"Expected to move one active benchmark label; changed {n}")

p.write_text(s2, encoding="utf-8")
