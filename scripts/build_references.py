"""Replace methodology cards while retaining the existing reference-page design."""
from pathlib import Path
import re
ROOT=Path(__file__).resolve().parents[1]
p=ROOT/'references.html'
s=p.read_text()
start=re.search(r'<article\b',s).start()
end=s.rindex('</article>')+len('</article>')
articles=re.findall(r'<article\b.*?</article>',s,re.S)
keep_ids=['raleigh-rent-trend','federal-minimum-wage','ncsu-affordable-supportive-housing','ncsu-dining-10-wage','ncsu-fws-15-current','ncsu-dining-current-wage','ncsu-2024-food-housing-report','map-basemap-attribution','ncsu-housing-rates-2026-27']
kept=[a for a in articles if any(f'id="{id}"' in a for id in keep_ids)]
for i,a in enumerate(kept):
    if 'ncsu-housing-rates-2026-27' not in a and 'map-basemap-attribution' not in a and '<strong>Supporting reporting source.</strong>' not in a:
        a=a.replace('<div class="ref-body">','<div class="ref-body"><p class="use-note"><strong>Supporting reporting source.</strong> Retained from the original reference log. Historical wage, survey and market figures below are background; they are not inputs to the revised rent or personal-resource calculations above.</p>',1)
    kept[i]=a
new=(ROOT/'docs/revised-methods.html').read_text()+'\n'+'\n'.join(kept)
s=s[:start]+new+s[end:]
s=s.replace('Working source log for data, quotes, methodology and supporting evidence used in the NC State rent article. Add new references here as reporting continues.', 'Source snapshot: September 9, 2026. Analysis revised September 13, 2026. Start with the worked math, then inspect the Excel audit and individual review decisions. Supporting reporting sources are retained below.')
s=s.replace('<h1>Reporting references</h1>','<h1>References & step-by-step math</h1>')
s=re.sub(r'<nav class="method-nav">.*?</nav>', '', s, flags=re.S)
s=re.sub(r'<div class="deck">.*?</div>', '<div class="deck">September 9, 2026 advertised-price snapshot, reviewed September 13. Start with the room-only Excel audit to follow the saved data through the listing counts, sums and averages. Sources and assumptions for the earnings and aid comparison follow below.</div>', s, count=1, flags=re.S)
scripts='<script src="assets/reviewed-data.js"></script>\n<script src="assets/rent-analysis.js"></script>\n<script src="assets/reference-math.js"></script>\n'
if 'src="assets/reference-math.js' not in s: s=s.replace('<script>',scripts+'<script>',1)
if '.method-scroll{' not in s:
    s=s.replace('</style>','.method-scroll{overflow-x:auto;margin:16px 0}.method-table{border-collapse:collapse;width:100%;font-size:12px}.method-table td,.method-table th{padding:10px;border-bottom:1px solid #ddd;text-align:left;vertical-align:top}.method-table th{background:#f4f1ec}.method-table td{min-width:90px}.method-table td:last-child{min-width:150px}.ref-body p,.ref-body li{line-height:1.65}.ref-body li{margin-bottom:9px}.method-nav{line-height:2;margin:16px 0}.audit-download{display:inline-block;padding:10px;background:#8b1f2d;color:white!important;border-radius:4px}details summary{cursor:pointer;font-weight:700}details[open] .method-table td:last-child{min-width:360px}</style>',1)
s=s.replace('https://www.bls.gov/news.release/cpi.htm','https://www.bls.gov/news.release/archives/cpi_08122026.htm')
if '.ref{scroll-margin-top:130px}' not in s: s=s.replace('</style>', '.ref{scroll-margin-top:130px}</style>',1)
# Keep the workbook download inside its own audit reference entry.
s=re.sub(r'<p class="reference-download-top">.*?</p>', '', s, flags=re.S)
# A changed page must not reuse the prior calculator or workbook from browser cache.
for asset in ['assets/rent-analysis.js','assets/reference-math.js','data/audits/ncsu-rent-audit.xlsx']:
    version='20260913-kept2' if asset.endswith('.xlsx') else '20260913-room-methods'
    s=re.sub(re.escape(asset)+r'(?:\?v=[^"\s]*)?(?=")', asset+'?v='+version, s)
p.write_text(s)
