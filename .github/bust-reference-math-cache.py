from pathlib import Path
p=Path('references.html')
s=p.read_text(encoding='utf-8')
s=s.replace('assets/reference-math.js?v=20260913-room-methods','assets/reference-math.js?v=20260915-resnet-toggle',1)
p.write_text(s,encoding='utf-8')
