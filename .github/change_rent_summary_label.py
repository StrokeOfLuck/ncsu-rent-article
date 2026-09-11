from pathlib import Path
p=Path('index.html')
s=p.read_text(encoding='utf-8')
old='`${campuses[currentCampusKey].label} · equal-weight average of the 0–1, >1–3 and >3–5 mile distance-band means`'
new='`${campuses[currentCampusKey].label} · average of the three distance-band rent estimates`'
if old not in s:
    raise SystemExit('target text not found')
s=s.replace(old,new,1)
p.write_text(s,encoding='utf-8')
print('updated rent summary label')
