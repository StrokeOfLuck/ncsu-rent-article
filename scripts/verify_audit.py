"""Regression checks for the published price analysis and the actual exported XLSX."""
import csv,hashlib,json,math,re,subprocess,os,tempfile,zipfile
from pathlib import Path
from html.parser import HTMLParser
import xml.etree.ElementTree as ET
root=Path(__file__).resolve().parents[1]
d=json.loads((root/'data/reviewed-rentals.json').read_text());rs=d['rentals'];ns={'s':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
for name,h in d['raw_sha256'].items():assert hashlib.sha256((root/'data'/name).read_bytes()).hexdigest()==h
assert len(rs)==168 and len({r['site_id'] for r in rs})==168
union=[r for r in rs if r['in_union']];assert len(union)==156
assert sum(r['eligible_price'] for r in union)==131
assert sum(r['pricing_type']!=r['original_pricing_type'] and r['pricing_type']!='Review' for r in rs)==23
assert not next(r for r in rs if r['site_id']=='z44390w')['eligible_price']
assert next(r for r in rs if r['site_id']=='lpl9fce')['pricing_type']=='Per bedroom'
assert next(r for r in rs if r['site_id']=='70rqkwy')['band_centennial']=='>3–5 mi'
def stats(rows,cat):
 a=[r for r in rows if r['eligible_price'] and r['pricing_type']==cat]
 n=len(a);lo=sum(r['rent_low'] for r in a);hi=sum(r['rent_high'] for r in a)
 return n,lo,hi,lo/n if n else None,hi/n if n else None,(lo+hi)/(2*n) if n else None
z=zipfile.ZipFile(root/'data/audits/ncsu-rent-audit.xlsx')
shared=[]
if 'xl/sharedStrings.xml' in z.namelist():
 for item in ET.fromstring(z.read('xl/sharedStrings.xml')).findall('s:si',ns):shared.append(''.join(t.text or '' for t in item.findall('.//s:t',ns)))
def cells(sheet):
 r=ET.fromstring(z.read(f'xl/worksheets/sheet{sheet}.xml'));out={}
 for c in r.findall('.//s:c',ns):
  assert c.get('t')!='e',(sheet,c.attrib,ET.tostring(c))
  val=c.findtext('s:v',namespaces=ns)
  if c.get('t')=='s':val=shared[int(val)] if val is not None else ''
  elif c.get('t')=='inlineStr':val=''.join(t.text or '' for t in c.findall('.//s:t',ns))
  elif val is not None and c.get('t') not in ['str']:val=float(val)
  out[c.get('r')]=val
 return out
sheets={n:cells(n) for n in range(1,9)}
sets=[]
for k in d['campuses']:
 for lo,hi in [(0,1),(1,3),(3,5),(0,5)]:sets.append([r for r in rs if (r['distance_'+k]>=0 if lo==0 else r['distance_'+k]>lo) and r['distance_'+k]<=hi])
sets.append(union)
i=2
for rows in sets:
 for cat in ['Per bedroom','Whole unit']:
  v=stats(rows,cat);assert sheets[5]['D'+str(i)]==len(rows)
  for col,expected in zip('EFGHIJ',v):assert math.isclose(sheets[5][col+str(i)],expected,abs_tol=1e-7),(i,col,expected)
  assert sheets[5]['K'+str(i)]==sum(not r['eligible_price'] for r in rows)
  i+=1
for i,r in enumerate(rs,2):
 assert sheets[4]['O'+str(i)]==int(r['eligible_price'])
 for c,k in [('P','main'),('R','centennial'),('T','vet')]:assert math.isclose(sheets[4][c+str(i)],r['distance_'+k],abs_tol=1e-8)
assert math.isclose(sheets[7]['B19'],stats(union,'Per bedroom')[-1]/1300,abs_tol=1e-10)
assert math.isclose(sheets[8]['B18'],8240/9,abs_tol=1e-10)
assert math.isclose(sheets[7]['B44'],1300,abs_tol=1e-10)
for row,resources in [(50,1300),(51,1300+14743/12),(52,1300+4106/12),(53,1300+(14743+4106)/12)]:
 assert math.isclose(sheets[7]['B'+str(row)],resources,abs_tol=1e-9)
 assert math.isclose(sheets[7]['C'+str(row)],stats(union,'Per bedroom')[-1]/resources,abs_tol=1e-10)
class HTML(HTMLParser):
 def __init__(self):super().__init__();self.ids=[];self.links=[];self.inputs={}
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if 'id' in a:self.ids.append(a['id'])
  if tag in ['script','link','a']:
   href=a.get('href',a.get('src',''))
   if href:self.links.append(href)
  if tag=='input' and 'id' in a:self.inputs[a['id']]=a
node=os.getenv('CODEX_PRIMARY_RUNTIME_NODE','node')
for f in ['index.html','references.html','rental-map-audit.html','rental-map-audit-original.html']:
 text=(root/f).read_text();h=HTML();h.feed(text);assert len(h.ids)==len(set(h.ids)),f+' duplicate IDs'
 for href in h.links:
  if href.startswith(('https:','http:','data:','mailto:')):continue
  file,_,anchor=href.partition('#');target=root/(file or f)
  assert target.exists(),(f,href)
  if anchor and target.suffix=='.html':
   other=HTML();other.feed(target.read_text());assert anchor in other.ids,(f,href,'missing anchor')
 assert not any(old in text for old in ['equal-weight average','$55,492.00','$147,564.00','XLSX.utils']),f+' stale calculation'
 for j,script in enumerate(re.findall(r'<script>(.*?)</script>',text,re.S)):
  path=Path(tempfile.gettempdir())/f'ncsu-{f}-{j}.js';path.write_text(script);subprocess.run([node,'--check',str(path)],check=True,capture_output=True)
 if f=='index.html':
  (Path(tempfile.gettempdir())/'ncsu-dom.json').write_text(json.dumps({'ids':h.ids,'inputs':h.inputs}))
print('PASS: 168 records, source hashes, 26 geography/category summaries, 504 distances, workbook cached results, budget/rate math, local links, unique IDs and JS syntax.')
