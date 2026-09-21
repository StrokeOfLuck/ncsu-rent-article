#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
import json, math, zipfile
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[1]
DATA = json.loads((ROOT / "data/reviewed-rentals.json").read_text(encoding="utf-8"))
OUT = ROOT / "data/audits/ncsu-room-rent-audit.xlsx"

all_rows = DATA["rentals"]
rooms = [r for r in all_rows if r.get("in_union") and r.get("eligible_price") and r.get("pricing_type") == "Per bedroom"]
room_ids = {r["site_id"] for r in rooms}
excluded = [r for r in all_rows if r["site_id"] not in room_ids]
assert len(rooms) == 76
assert len(excluded) == 92

def col(n:int)->str:
    s=""
    while n:
        n, rem = divmod(n-1,26)
        s = chr(65+rem)+s
    return s

def xesc(v):
    return escape(str(v), {'"': '&quot;', "'": '&apos;'})

# style ids: 0 normal, 1 header, 2 money, 3 decimal, 4 bold, 5 wrap, 6 title
def cxml(ref, value=None, style=0, formula=None):
    st = f' s="{style}"' if style else ""
    if formula is not None:
        v = "" if value is None else f"<v>{value}</v>"
        return f'<c r="{ref}"{st}><f>{xesc(formula)}</f>{v}</c>'
    if value is None or value == "":
        return f'<c r="{ref}"{st}/>'
    if isinstance(value, bool):
        return f'<c r="{ref}"{st} t="b"><v>{1 if value else 0}</v></c>'
    if isinstance(value, (int,float)) and math.isfinite(float(value)):
        return f'<c r="{ref}"{st}><v>{value}</v></c>'
    return f'<c r="{ref}"{st} t="inlineStr"><is><t xml:space="preserve">{xesc(value)}</t></is></c>'

def sheet_xml(rows, widths=None, freeze=1, autofilter=None):
    parts = ['<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
             '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">']
    if freeze:
        parts.append(f'<sheetViews><sheetView workbookViewId="0"><pane ySplit="{freeze}" topLeftCell="A{freeze+1}" activePane="bottomLeft" state="frozen"/></sheetView></sheetViews>')
    else:
        parts.append('<sheetViews><sheetView workbookViewId="0"/></sheetViews>')
    if widths:
        parts.append("<cols>")
        for i,w in enumerate(widths,1):
            parts.append(f'<col min="{i}" max="{i}" width="{w}" customWidth="1"/>')
        parts.append("</cols>")
    parts.append("<sheetData>")
    for ri,row in enumerate(rows,1):
        parts.append(f'<row r="{ri}">')
        for ci,item in enumerate(row,1):
            if isinstance(item, dict):
                parts.append(cxml(f"{col(ci)}{ri}", item.get("v"), item.get("s",0), item.get("f")))
            else:
                parts.append(cxml(f"{col(ci)}{ri}", item))
        parts.append("</row>")
    parts.append("</sheetData>")
    if autofilter:
        parts.append(f'<autoFilter ref="{autofilter}"/>')
    parts.append("</worksheet>")
    return "".join(parts)

def H(v): return {"v":v,"s":1}
def M(v,f=None): return {"v":v,"s":2,"f":f}
def D(v,f=None): return {"v":v,"s":3,"f":f}
def B(v,f=None): return {"v":v,"s":4,"f":f}
def W(v): return {"v":v,"s":5}
def T(v): return {"v":v,"s":6}

sheets = []

# Listings
headers = ["Listing ID","Listing name","Source URL","Reviewed basis","Latitude","Longitude","Low ($/mo)","High ($/mo)","Midpoint ($/mo)","Main distance (mi)","Main band","Centennial distance (mi)","Centennial band","Biomedical distance (mi)","Biomedical band","In union","Room audit","Review status / reason"]
rows = [[H(x) for x in headers]]
for i,r in enumerate(all_rows,2):
    rows.append([
        r["site_id"],r["name"],r["listing_url"],r["pricing_type"],D(r["lat"]),D(r["lon"]),
        M(r["rent_low"]),M(r["rent_high"]),M((r["rent_low"]+r["rent_high"])/2,f"(G{i}+H{i})/2"),
        D(r["distance_main"]),r["band_main"],D(r["distance_centennial"]),r["band_centennial"],
        D(r["distance_vet"]),r["band_vet"],1 if r["in_union"] else 0,1 if r["site_id"] in room_ids else 0,
        W(" | ".join(x for x in [r.get("review_status",""),r.get("exclusion_reason",""),r.get("review_note","")] if x))
    ])
sheets.append(("Listings",sheet_xml(rows,[16,36,54,18,14,14,14,14,16,16,16,18,16,18,16,10,12,72],1,f"A1:R{len(rows)}")))

def band_sheet(name, rs, key=None):
    rows = [[T(name)],[W("Sept. 9, 2026 advertised-price snapshot. One vote per listing; midpoint=(low+high)/2.")],[],
            [H(x) for x in (["Listing name","Low ($/month)","High ($/month)","Midpoint ($/month)",("Distance (mi)" if key else "Main distance (mi)"),"Listing ID","Source URL"] + ([] if key else ["Centennial distance (mi)","Biomedical distance (mi)"]))]]
    start = 5
    for j,r in enumerate(rs,start):
        base = [r["name"],M(r["rent_low"]),M(r["rent_high"]),M((r["rent_low"]+r["rent_high"])/2,f"(B{j}+C{j})/2"),
                D(r[f"distance_{key}"] if key else r["distance_main"]),r["site_id"],r["listing_url"]]
        if not key:
            base += [D(r["distance_centennial"]),D(r["distance_vet"])]
        rows.append(base)
    last = start + len(rs) - 1
    count = last + 2
    total = last + 3
    mean = last + 4
    median = last + 5
    while len(rows) < median:
        rows.append([])
    lows=[r["rent_low"] for r in rs]; highs=[r["rent_high"] for r in rs]; mids=[(r["rent_low"]+r["rent_high"])/2 for r in rs]
    mids_sorted=sorted(mids)
    med=(mids_sorted[(len(mids_sorted)-1)//2] if len(mids_sorted)%2 else (mids_sorted[len(mids_sorted)//2-1]+mids_sorted[len(mids_sorted)//2])/2)
    rows[count-1]=[B("Prices used (COUNT)"),B(len(rs),f"COUNT(B{start}:B{last})"),B(len(rs),f"COUNT(C{start}:C{last})"),B(len(rs),f"COUNT(D{start}:D{last})")]
    rows[total-1]=[B("Total advertised rent (SUM)"),M(sum(lows),f"SUM(B{start}:B{last})"),M(sum(highs),f"SUM(C{start}:C{last})"),M(sum(mids),f"SUM(D{start}:D{last})")]
    rows[mean-1]=[B("Average (sum / count)"),M(sum(lows)/len(rs),f"B{total}/B{count}"),M(sum(highs)/len(rs),f"C{total}/C{count}"),M(sum(mids)/len(rs),f"D{total}/D{count}")]
    rows[median-1]=[B("Median listing midpoint"),None,None,M(med,f"MEDIAN(D{start}:D{last})")]
    widths=[38,16,16,18,16,16,54] + ([] if key else [18,18])
    return rows, dict(start=start,last=last,count=count,total=total,mean=mean,median=median,
                      avg_low=sum(lows)/len(rs),avg_high=sum(highs)/len(rs),avg_mid=sum(mids)/len(rs))

rooms_sorted=sorted(rooms,key=lambda r:r["name"].lower())
room_rows, room_meta = band_sheet("Rooms union - 76 unique room listings",rooms_sorted,None)
sheets.append(("Rooms",sheet_xml(room_rows,[38,16,16,18,16,16,54,18,18],4,f"A4:I{room_meta['last']}")))

# Main Campus analytic sample - the exact 74 listings used in the article.
main_sample=[r for r in rooms_sorted if r["distance_main"]<=5]
assert len(main_sample)==74

main_rows=[
    [T("Main Campus analytic sample - 74 room listings")],
    [W("September 9, 2026 advertised-price snapshot; bedroom-occupancy classifications reviewed September 20. This is the exact 74-listing Main Campus sample used in the article: 18 listings at 0-1 mile, 46 at >1-3 miles and 10 at >3-5 miles.")],
    [],
    [H(x) for x in ["Listing name","Low ($/month)","High ($/month)","Midpoint ($/month)","Main distance (mi)","Main band","Listing ID","Source URL"]]
]
main_start=5
for j,r in enumerate(main_sample,main_start):
    d=r["distance_main"]
    band="0-1 mi" if d<=1 else ("1-3 mi" if d<=3 else "3-5 mi")
    main_rows.append([
        r["name"], M(r["rent_low"]), M(r["rent_high"]),
        M((r["rent_low"]+r["rent_high"])/2,f"(B{j}+C{j})/2"),
        D(d), band, r["site_id"], r["listing_url"]
    ])

# Keep two blank rows between the listing table and the audit math.
while len(main_rows)<80:
    main_rows.append([])

main_rows.append([T("Main Campus distance-band math")])
main_rows.append([H(x) for x in ["Band","Listings","Low-price sum","High-price sum","Midpoint sum","Mean midpoint"]])

main_band_defs=[("0-1 mi",0,1),("1-3 mi",1,3),("3-5 mi",3,5)]
summary_start=83
for idx,(label,low,high) in enumerate(main_band_defs,summary_start):
    rs=[r for r in main_sample if r["distance_main"]<=high and (low==0 or r["distance_main"]>low)]
    low_sum=sum(r["rent_low"] for r in rs)
    high_sum=sum(r["rent_high"] for r in rs)
    mid_sum=sum((r["rent_low"]+r["rent_high"])/2 for r in rs)
    main_rows.append([
        B(label),
        {"v":len(rs),"f":f'COUNTIF(F{main_start}:F78,A{idx})'},
        M(low_sum,f'SUMIF(F{main_start}:F78,A{idx},B{main_start}:B78)'),
        M(high_sum,f'SUMIF(F{main_start}:F78,A{idx},C{main_start}:C78)'),
        M(mid_sum,f'SUMIF(F{main_start}:F78,A{idx},D{main_start}:D78)'),
        M(mid_sum/len(rs),f'E{idx}/B{idx}')
    ])

main_low=sum(r["rent_low"] for r in main_sample)
main_high=sum(r["rent_high"] for r in main_sample)
main_mid=sum((r["rent_low"]+r["rent_high"])/2 for r in main_sample)
main_rows.append([
    B("Main Campus total"),
    B(len(main_sample),f"SUM(B83:B85)"),
    M(main_low,f"SUM(C83:C85)"),
    M(main_high,f"SUM(D83:D85)"),
    M(main_mid,f"SUM(E83:E85)"),
    M(main_mid/len(main_sample),f"E86/B86")
])
main_rows.append([])
main_rows.append([B("Article check"),W("18 + 46 + 10 = 74 listings. Midpoint sum = $64,271.50; $64,271.50 / 74 = $868.53/month, displayed in the article as about $869.")])
main_rows.append([B("Scope"),W("One portal listing ID receives one vote. Advertised prices may exclude utilities and fees. This sheet excludes the two cross-campus-only room listings that are outside the five-mile Main Campus sample.")])

sheets.append(("Main sample (74)",sheet_xml(main_rows,[38,16,16,18,16,14,16,54],4,"A4:H78")))

band_specs=[]
for key in ("main","centennial","vet"):
    prefix={"main":"Main","centennial":"Centennial","vet":"Biomedical"}[key]
    for low,high,label in ((0,1,"0-1 mi"),(1,3,"1-3 mi"),(3,5,"3-5 mi")):
        rs=[r for r in rooms_sorted if r[f"distance_{key}"]<=high and (low==0 or r[f"distance_{key}"]>low)]
        name=f"{prefix} {label}"
        br,bm=band_sheet(name,rs,key)
        band_specs.append((prefix,name,rs,bm))
        sheets.append((name,sheet_xml(br,[38,16,16,18,16,16,54],4,f"A4:G{bm['last']}")))

assert [len(rs) for p,n,rs,m in band_specs if p=="Main"] == [18,46,10]

# Excluded
def exclusion_reason(r):
    out=[]
    if not r.get("in_union"): out.append("Outside all three five-mile areas")
    if not r.get("eligible_price"): out.append(r.get("exclusion_reason") or "Invalid price pair")
    if r.get("pricing_type")!="Per bedroom":
        out.append("Whole-unit offer, outside room-only scope" if r.get("pricing_type")=="Whole unit" else "Not a resolved room/per-bedroom offer")
    return ". ".join(out or ["Outside final room-audit membership"]) + "."
erows=[[H(x) for x in ["Listing name","Reviewed basis","Reason excluded from room article","Listing ID","Source URL","Review evidence"]]]
for r in sorted(excluded,key=lambda r:r["name"].lower()):
    erows.append([r["name"],r["pricing_type"],W(exclusion_reason(r)),r["site_id"],r["listing_url"],W(r.get("review_note") or r.get("review_status") or "")])
sheets.append(("Excluded",sheet_xml(erows,[38,18,58,16,54,72],1,f"A1:F{len(erows)}")))

# Summary
srows=[[T("Room rent audit")],[W("September 9, 2026 advertised-price snapshot; classifications reviewed September 20.")],[],
       [H(x) for x in ["Campus / distance","Room listings","Low-price sum","High-price sum","Average low","Average high","Mean midpoint"]]]
excel_row=5
for prefix in ("Main","Centennial","Biomedical"):
    specs=[x for x in band_specs if x[0]==prefix]
    start=excel_row
    merged=[]
    for _,name,rs,m in specs:
        low=sum(r["rent_low"] for r in rs); high=sum(r["rent_high"] for r in rs)
        srows.append([name,
                      {"v":len(rs),"f":f"'{name}'!B{m['count']}"},
                      M(low,f"'{name}'!B{m['total']}"),M(high,f"'{name}'!C{m['total']}"),
                      M(m["avg_low"],f"'{name}'!B{m['mean']}"),M(m["avg_high"],f"'{name}'!C{m['mean']}"),M(m["avg_mid"],f"'{name}'!D{m['mean']}")])
        merged += rs
        excel_row += 1
    end=excel_row-1
    cnt=len(merged); low=sum(r["rent_low"] for r in merged); high=sum(r["rent_high"] for r in merged)
    srows.append([B(f"{prefix} Campus total"),B(cnt,f"SUM(B{start}:B{end})"),M(low,f"SUM(C{start}:C{end})"),M(high,f"SUM(D{start}:D{end})"),
                  M(low/cnt,f"C{excel_row}/B{excel_row}"),M(high/cnt,f"D{excel_row}/B{excel_row}"),M((low+high)/(2*cnt),f"(E{excel_row}+F{excel_row})/2")])
    excel_row += 1
srows.append([B("All three areas, unique IDs"),B(len(rooms),f"'Rooms'!B{room_meta['count']}"),
              M(sum(r["rent_low"] for r in rooms),f"'Rooms'!B{room_meta['total']}"),
              M(sum(r["rent_high"] for r in rooms),f"'Rooms'!C{room_meta['total']}"),
              M(room_meta["avg_low"],f"'Rooms'!B{room_meta['mean']}"),M(room_meta["avg_high"],f"'Rooms'!C{room_meta['mean']}"),M(room_meta["avg_mid"],f"'Rooms'!D{room_meta['mean']}")])
srows += [[],[B("Article check"),W("Main Campus: 18 + 46 + 10 = 74 listings; mean midpoint = $868.53, displayed as about $869.")],
          [B("Scope"),W("Room/per-bedroom advertised offers within five miles of at least one campus point. Campus areas overlap; do not add campus totals.")],
          [B("Price note"),W("Advertised prices may exclude utilities and fees. Each listing receives equal weight.")]]
sheets.append(("Summary",sheet_xml(srows,[34,16,18,18,18,18,18],4,None)))

# Desired sheet order.
order=["Summary","Rooms","Main sample (74)"]+[name for _,name,_,_ in band_specs]+["Excluded","Listings"]
sheet_map=dict(sheets)
sheets=[(name,sheet_map[name]) for name in order]
assert len(sheets)==14

styles='''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">
<numFmts count="1"><numFmt numFmtId="164" formatCode="$#,##0.00"/></numFmts>
<fonts count="3"><font><sz val="10"/><name val="Arial"/></font><font><b/><color rgb="FFFFFFFF"/><sz val="10"/><name val="Arial"/></font><font><b/><sz val="10"/><name val="Arial"/></font></fonts>
<fills count="4"><fill><patternFill patternType="none"/></fill><fill><patternFill patternType="gray125"/></fill><fill><patternFill patternType="solid"><fgColor rgb="FF2D485D"/><bgColor indexed="64"/></patternFill></fill><fill><patternFill patternType="solid"><fgColor rgb="FFE8EEF2"/><bgColor indexed="64"/></patternFill></fill></fills>
<borders count="1"><border><left/><right/><top/><bottom/><diagonal/></border></borders>
<cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs>
<cellXfs count="7">
<xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/>
<xf numFmtId="0" fontId="1" fillId="2" borderId="0" xfId="0" applyFill="1" applyFont="1" applyAlignment="1"><alignment wrapText="1" vertical="center"/></xf>
<xf numFmtId="164" fontId="0" fillId="0" borderId="0" xfId="0" applyNumberFormat="1"/>
<xf numFmtId="4" fontId="0" fillId="0" borderId="0" xfId="0" applyNumberFormat="1"/>
<xf numFmtId="0" fontId="2" fillId="3" borderId="0" xfId="0" applyFill="1" applyFont="1"/>
<xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0" applyAlignment="1"><alignment wrapText="1"/></xf>
<xf numFmtId="0" fontId="2" fillId="0" borderId="0" xfId="0" applyFont="1"/>
</cellXfs>
<cellStyles count="1"><cellStyle name="Normal" xfId="0" builtinId="0"/></cellStyles>
</styleSheet>'''

workbook='<?xml version="1.0" encoding="UTF-8" standalone="yes"?><workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets>'+''.join(f'<sheet name="{xesc(name)}" sheetId="{i}" r:id="rId{i}"/>' for i,(name,_) in enumerate(sheets,1))+'</sheets><calcPr calcId="191029" calcMode="auto" fullCalcOnLoad="1" forceFullCalc="1"/></workbook>'
rels='<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'+''.join(f'<Relationship Id="rId{i}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet{i}.xml"/>' for i in range(1,len(sheets)+1))+f'<Relationship Id="rId{len(sheets)+1}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/></Relationships>'
root_rels='<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/></Relationships>'
ct='<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/><Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>'+''.join(f'<Override PartName="/xl/worksheets/sheet{i}.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>' for i in range(1,len(sheets)+1))+'</Types>'

OUT.parent.mkdir(parents=True,exist_ok=True)
with zipfile.ZipFile(OUT,"w",compression=zipfile.ZIP_DEFLATED) as z:
    z.writestr("[Content_Types].xml",ct)
    z.writestr("_rels/.rels",root_rels)
    z.writestr("xl/workbook.xml",workbook)
    z.writestr("xl/_rels/workbook.xml.rels",rels)
    z.writestr("xl/styles.xml",styles)
    for i,(_,xml) in enumerate(sheets,1):
        z.writestr(f"xl/worksheets/sheet{i}.xml",xml)

# Structural validation and key article numbers.
with zipfile.ZipFile(OUT) as z:
    bad=z.testzip()
    assert bad is None, bad
    assert "xl/workbook.xml" in z.namelist()
    assert len([n for n in z.namelist() if n.startswith("xl/worksheets/sheet")])==14
main=[r for r in rooms if r["distance_main"]<=5]
mean=sum((r["rent_low"]+r["rent_high"])/2 for r in main)/len(main)
assert len(main)==74 and abs(mean-868.5337837837837)<1e-8
print(f"Wrote {OUT} with {len(sheets)} sheets; Main Campus {len(main)} listings, mean {mean:.2f}.")
