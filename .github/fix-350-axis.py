from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')
old='''.burden-axis-scale .axis-350 {
  left:100%;
  transform:translateX(-100%);
}'''
new='''.burden-axis-scale .axis-350 {
  left:auto;
  right:0;
  transform:none;
  text-align:right;
}'''
if old in s:
    s=s.replace(old,new,1)
elif 'right:0;\n  transform:none;\n  text-align:right;' not in s:
    raise SystemExit('Expected 350% axis rule not found')
p.write_text(s,encoding='utf-8')
