/** Author the downloadable audit with @oai/artifact-tool. Source CSVs remain intact. */
import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { Workbook, SpreadsheetFile } from '@oai/artifact-tool';
import A from '../assets/rent-analysis.js';
const root=path.dirname(path.dirname(fileURLToPath(import.meta.url)));
const d=JSON.parse(await fs.readFile(path.join(root,'data/reviewed-rentals.json'),'utf8'));
const raw=JSON.parse(await fs.readFile(path.join(root,'data/audits/source-tables.json'),'utf8'));
const out=path.join(root,'data/audits'), qa=process.env.RENT_AUDIT_QA_DIR||'/tmp/ncsu-rent-workbook-qa';
await fs.mkdir(qa,{recursive:true});
const wb=Workbook.create();
const names=['Guide','Raw properties','Raw floorplans','Listings','Summary','Sensitivity','Budget','Housing rates'];
const sheets=Object.fromEntries(names.map(name=>[name,wb.worksheets.add(name)]));
const money='$#,##0.00;($#,##0.00);"$0.00"', percent='0.00%';
function col(i){let s='';for(i++;i;i=Math.floor((i-1)/26))s=String.fromCharCode(65+(i-1)%26)+s;return s;}
function block(sh,headers,rows){sh.getRange(`A1:${col(headers.length-1)}1`).values=[headers];if(rows.length)sh.getRange(`A2:${col(headers.length-1)}${rows.length+1}`).values=rows;
 sh.getRange(`A1:${col(headers.length-1)}${rows.length+1}`).format.font={name:'Arial',size:10};
 sh.getRange(`A1:${col(headers.length-1)}1`).format={fill:'#2D485D',font:{name:'Arial',bold:true,color:'#FFFFFF'},rowHeight:38,wrapText:true};
 sh.getRange(`A:${col(headers.length-1)}`).format.columnWidth=17; sh.freezePanes.freezeRows(1);sh.showGridLines=false;
}
function formula(sh,address,text){sh.getRange(address).formulas=[[text]];}
function note(sh,address,text){wb.notes.add({id:sh.name+':'+address,target:{cell:{sheetName:sh.name,sheetId:sh.sheetId,address}},authorId:'',createdAt:'',body:{plainText:text}});}
// Preserve raw values, including 0 placeholders and blank endpoints. Selected numeric source columns become numbers.
for(const [sheet,key,numeric] of [['Raw properties','properties',['latitude','longitude','rent_low','rent_high','beds_low','beds_high','total_units']],['Raw floorplans','floorplans',['price_low','price_high','beds','baths','units_available']]]) {
 const headers=Object.keys(raw[key][0]);
 const rs=raw[key].map(r=>headers.map(h=>numeric.includes(h)&&r[h]!==''&&Number.isFinite(Number(r[h]))?Number(r[h]):r[h]));
 const sh=sheets[sheet];block(sh,headers,rs);sh.getRange('A:C').format.columnWidth=19;
 if(sheet==='Raw properties'){sh.getRange('D:D').format.columnWidth=42;sh.getRange('E:E').format.columnWidth=36;sh.getRange('D2:E'+(rs.length+1)).format.wrapText=true;sh.getRange('D2:E'+(rs.length+1)).format.autofitRows();}
 else {sh.getRange('B:B').format.columnWidth=42;sh.getRange('E:E').format.columnWidth=32;sh.getRange('B2:B'+(rs.length+1)).format.wrapText=true;sh.getRange('B2:B'+(rs.length+1)).format.autofitRows();}
 sh.tables.add(`A1:${col(headers.length-1)}${rs.length+1}`,true,sheet==='Raw properties'?'RawProperties':'RawFloorplans');
}
const pheaders=Object.keys(raw.properties[0]), rawCol=k=>col(pheaders.indexOf(k));
const fheaders=Object.keys(raw.floorplans[0]), fcol=k=>col(fheaders.indexOf(k));
const fprange=k=>`'Raw floorplans'!$${fcol(k)}$2:$${fcol(k)}$${raw.floorplans.length+1}`;
const ls=sheets.Listings;
const headers=['Listing ID','Listing name','Source URL','Original basis','Reviewed basis','Latitude','Longitude','Source low ($/mo)','Source high ($/mo)','Floor-plan low ($/mo)','Floor-plan high ($/mo)','Basis review flag','Price mismatch flag','Valid price pair','Use price (1=yes)','Main distance (mi)','Main band','Centennial distance (mi)','Centennial band','Biomedical distance (mi)','Biomedical band','In combined 5 mi','Included midpoint ($/mo)','Use in combined mean','All plans 2027+','Waitlist mentioned','Endpoint review flag','All-in price differs','Source sublet flag','Source lease term','Earliest saved date','Price status','Review evidence / reason','Source rent display','Main edge (feet)','Centennial edge (feet)','Biomedical edge (feet)','Within 100 feet of edge'];
const rows=d.rentals.map(r=>[r.site_id,r.name,r.listing_url,r.original_pricing_type,r.pricing_type,r.lat,r.lon,r.rent_low,r.rent_high,r.floorplan_low,r.floorplan_high,+r.flags.includes('pricing_basis_review'),null,null,null,null,null,null,null,null,null,null,null,null,+r.all_2027_or_later,+r.flags.includes('waitlist_mentioned'),+r.flags.includes('high_endpoint_review'),+r.all_in_differs,+r.sublet,r.lease_term,r.earliest_date,r.review_status,r.review_note,r.rent_display,null,null,null,null]);
block(ls,headers,rows);const end=rows.length+1;
ls.getRange('B:B').format.columnWidth=40;ls.getRange('C:C').format.columnWidth=22;ls.getRange('D:E').format.columnWidth=20;ls.getRange('AG:AG').format.columnWidth=90;
ls.getRange(`AG2:AG${end}`).format.wrapText=true;ls.getRange(`A2:AL${end}`).format.rowHeight=44;
ls.getRange(`H2:K${end}`).setNumberFormat(money);ls.getRange(`W2:W${end}`).setNumberFormat(money);ls.getRange(`F2:G${end}`).setNumberFormat('0.000000');
for(const c of ['P','R','T']) ls.getRange(`${c}2:${c}${end}`).setNumberFormat('0.000000');
ls.getRange(`AI2:AK${end}`).setNumberFormat('0.00');
for(let i=2;i<=end;i++) {
 for(const [target,key] of [['A','site_id'],['B','name'],['C','listing_url'],['F','latitude'],['G','longitude'],['H','rent_low'],['I','rent_high'],['AD','lease_term']]) {
 const ref=`'Raw properties'!${rawCol(key)}${i}`;formula(ls,target+i,`=IF(${ref}="","",${ref})`);}
 // Explicit source-cell references avoid MINIFS compatibility differences between Excel engines.
 const fi=raw.floorplans.map((f,j)=>f.site_id===d.rentals[i-2].site_id?j+2:null).filter(x=>x!==null);
 for(const [target,key,fn] of [['J','price_low','MIN'],['K','price_high','MAX']]) {
   const refs=fi.map(j=>`'Raw floorplans'!${fcol(key)}${j}`);
   const count=refs.map(ref=>`IF(${ref}>0,1,0)`).join('+');
   const terms=refs.map(ref=>`IF(${ref}>0,${ref},${fn==='MIN'?'1E99':'0'})`).join(',');
   formula(ls,target+i,`=IF((${count})=0,"",${fn}(${terms}))`);
 }
 formula(ls,`M${i}`,`=IF(AND(ISNUMBER(H${i}),ISNUMBER(I${i}),ISNUMBER(J${i}),ISNUMBER(K${i}),H${i}>0,I${i}>0),IF(OR(H${i}<>J${i},I${i}<>K${i}),1,0),0)`);
 formula(ls,`N${i}`,`=IF(AND(ISNUMBER(H${i}),ISNUMBER(I${i}),H${i}>0,I${i}>=H${i}),1,0)`);
 formula(ls,`O${i}`,`=IF(AND(L${i}=0,M${i}=0,N${i}=1),1,0)`);
 for(const [key,dc,bc,ec] of [['main','P','Q','AI'],['centennial','R','S','AJ'],['vet','T','U','AK']]){
 const c=d.campuses[key], lat=c.lat,lon=c.lon;
 formula(ls,dc+i,`=2*3958.7613*ASIN(SQRT(SIN(RADIANS(F${i}-${lat})/2)^2+COS(RADIANS(${lat}))*COS(RADIANS(F${i}))*SIN(RADIANS(G${i}-(${lon}))/2)^2))`);
 formula(ls,bc+i,`=IF(${dc}${i}<=1,"0–1 mi",IF(${dc}${i}<=3,">1–3 mi",IF(${dc}${i}<=5,">3–5 mi","Outside 5 mi")))`);
 formula(ls,ec+i,`=MIN(ABS(${dc}${i}-1),ABS(${dc}${i}-3),ABS(${dc}${i}-5))*5280`);
 }
 formula(ls,`V${i}`,`=IF(MIN(P${i},R${i},T${i})<=5,1,0)`);
 formula(ls,`W${i}`,`=IF(O${i}=1,(H${i}+I${i})/2,"")`);
 formula(ls,`X${i}`,`=O${i}*V${i}`);
 formula(ls,`AL${i}`,`=IF(MIN(AI${i},AJ${i},AK${i})<=100,1,0)`);
}
ls.getRange(`AG2:AG${end}`).format.autofitRows();
ls.tables.add(`A1:AL${end}`,true,'ReviewedListings');
ls.getRange(`O2:O${end}`).conditionalFormats.add('cellIs',{operator:'equal',formula:0,format:{fill:'#FCE8E6'}});
note(ls,'L1','Documented editorial exclusion input. Resolve pricing basis against evidence before changing from 1 to 0. See reviewed-rentals.json and review-decisions.json.');
note(ls,'J1','Envelope from saved floor-plan price_low fields. Used only to detect search/detail inconsistencies, not substitute rent.');
// Formula summaries: all three disjoint bands, pooled campuses and the combined union.
const summaryRows=[];
for(const [key,c] of Object.entries(d.campuses)) for(const [low,high,label] of [[0,1,'0–1 mi'],[1,3,'>1–3 mi'],[3,5,'>3–5 mi'],[0,5,'Pooled 0–5 mi']]) for(const type of ['Per bedroom','Whole unit']) summaryRows.push({key,campus:c.label,low,high,label,type});
for(const type of ['Per bedroom','Whole unit'])summaryRows.push({key:'union',campus:'All three campuses',low:0,high:5,label:'Unique-ID union',type});
const ss=sheets.Summary;
block(ss,['Geography','Band / pool','Category','Mapped IDs (all types)','Included n','Low-price sum ($)','High-price sum ($)','Low mean ($/mo)','High mean ($/mo)','Mean midpoint ($/mo)','Excluded IDs (all types)'],summaryRows.map(r=>[r.campus,r.label,r.type,null,null,null,null,null,null,null,null]));
ss.getRange('A:A').format.columnWidth=32;ss.getRange('B:C').format.columnWidth=20;ss.getRange('D:K').format.columnWidth=19;ss.getRange('F2:J27').setNumberFormat(money);
const range=c=>`Listings!$${c}$2:$${c}$${end}`;
function geoCriteria(r){if(r.key==='union')return `${range('V')},1`;const dc={main:'P',centennial:'R',vet:'T'}[r.key];return `${range(dc)},"${r.low===0?'>=':'>'}${r.low}",${range(dc)},"<=${r.high}"`;}
for(let j=0;j<summaryRows.length;j++){
 const r=summaryRows[j],i=j+2,g=geoCriteria(r),filter=`${g},${range('O')},1,${range('E')},C${i}`;
 formula(ss,'D'+i,`=COUNTIFS(${g})`);formula(ss,'E'+i,`=COUNTIFS(${filter})`);
 formula(ss,'F'+i,`=SUMIFS(${range('H')},${filter})`);formula(ss,'G'+i,`=SUMIFS(${range('I')},${filter})`);
 formula(ss,'H'+i,`=IF(E${i}=0,"",F${i}/E${i})`);formula(ss,'I'+i,`=IF(E${i}=0,"",G${i}/E${i})`);formula(ss,'J'+i,`=IF(E${i}=0,"",(H${i}+I${i})/2)`);
 formula(ss,'K'+i,`=COUNTIFS(${g},${range('O')},0)`);
}
ss.freezePanes.freezeRows(1);
// Explicit sensitivity selectors stay live as listing numeric inputs change.
const sn=sheets.Sensitivity;
const checks=[['Primary reviewed sample',''],['Omit all plans dated 2027+',`,${range('Y')},0`],['Omit waitlist mentions',`,${range('Z')},0`],['Omit flagged endpoint',`,${range('AA')},0`],['All three omissions',`,${range('Y')},0,${range('Z')},0,${range('AA')},0`]];
const sen=[];for(const [label,extra] of checks)for(const cat of ['Per bedroom','Whole unit'])sen.push({label,extra,cat});
block(sn,['Scenario','Category','Included n','Low sum ($)','High sum ($)','Low mean ($/mo)','High mean ($/mo)','Mean midpoint ($/mo)'],sen.map(r=>[r.label,r.cat,null,null,null,null,null,null]));sn.getRange('A:A').format.columnWidth=33;sn.getRange('B:B').format.columnWidth=21;sn.getRange('D2:H11').setNumberFormat(money);
for(let j=0;j<sen.length;j++){const r=sen[j],i=j+2,f=`${range('X')},1,${range('E')},B${i}${r.extra}`;formula(sn,'C'+i,`=COUNTIFS(${f})`);for(const [target,source] of [['D','H'],['E','I']])formula(sn,target+i,`=SUMIFS(${range(source)},${f})`);formula(sn,'F'+i,`=IF(C${i}=0,"",D${i}/C${i})`);formula(sn,'G'+i,`=IF(C${i}=0,"",E${i}/C${i})`);formula(sn,'H'+i,`=IF(C${i}=0,"",(F${i}+G${i})/2)`);}
// Budget: one common period and actual remaining living-expense funds, not CDS average awards.
const bs=sheets.Budget;
const budget=[
 ['Hourly wage ($/hour)',15,'Editable scenario; gross wage before tax.'],
 ['Hours per paid week',20,'General FWS guideline is no more than 20 hours; an individual award may restrict earnings further.'],
 ['Budget period (months)',12,'Use the same period for every total below.'],
 ['Requested paid weeks',52,'Illustrative availability of paid work, not a guarantee.'],
 ['Living-cost grant in period ($)',0,'After tuition, fees, account charges and other commitments; do not enter the entire average CDS grant.'],
 ['Living-cost loan in period ($)',0,'Borrowed funds remaining for living costs, not earnings.'],
 ['Other support in period ($)',0,'Family support, savings or other resources allocated to this period.'],
 ['Extra monthly housing costs ($)',0,'Only costs not already included in the advertised rent.'],
 ['Effective paid weeks',null,'Capped at 52 × months / 12 to fit the budget period.'],
 ['Work pay in period ($)',null,'Hourly wage × hours × effective paid weeks.'],
 ['Monthly gross work pay ($)',null,'Work pay / budget months.'],
 ['Monthly living-cost grant ($)',null,'Remaining living-cost grant / months.'],
 ['Monthly borrowed funds ($)',null,'Remaining loan / months.'],
 ['Monthly other support ($)',null,'Other support / months.'],
 ['Monthly resources ($)',null,'Pay + grant + loans + other. A budget illustration, not HUD household income.'],
 ['Room mean midpoint ($/mo)',null,'Linked to the combined-sample per-bedroom Summary result.'],
 ['Modeled monthly housing cost ($)',null,'Room mean midpoint + your extra housing costs.'],
 ['Housing / monthly resources',null,'Blank when resources are zero; not a formal HUD classification.'],
 ['Specific whole-unit rent ($/mo)',2400,'Separate lease example, not the mean across different dwelling sizes.'],
 ['Specific shared utilities ($/mo)',180,'Example only. Avoid double-counting included charges.'],
 ['Equal payers in that lease',3,'Use actual permitted occupants and agreed cost allocation.'],
 ['Specific lease share ($/mo)',null,'(Specific rent + shared utilities) / equal payers.'],
 ['Specific share / resources',null,'Personal lease share / monthly resources.'],
 ['Remaining FWS award cap ($)',3000,'Example cap; replace with actual remaining award for the period.'],
 ['FWS pay after award cap ($)',null,'Minimum of work pay in period and remaining FWS award.'],
 ['FWS monthly capped pay ($)',null,'Capped FWS pay / budget months; not automatically substituted for generic work above.'],
 ['Weeks supportable by award',null,'Award / (wage × hours); actual employment weeks may be fewer.'],
 ['CDS grant average, 2024–25 ($)',14743,'Historical recipient average in CDS 2025–26, H2 K. NOT a budget input.'],
 ['CDS need-loan average, 2024–25 ($)',4106,'Historical recipient average in CDS 2025–26, H2 M. Different recipient group. NOT a budget input.'],
 ['CDS grant / 12, context only ($)',null,'Scale illustration only; does not establish a refund available for housing.'],
 ['CDS loan / 12, context only ($)',null,'Scale illustration only; does not establish a typical combined aid package.']
];
block(bs,['Budget calculation','Value','Meaning / source'],budget);bs.getRange('A:A').format.columnWidth=42;bs.getRange('B:B').format.columnWidth=20;bs.getRange('C:C').format.columnWidth=91;bs.getRange('C2:C32').format.wrapText=true;bs.getRange('A2:C32').format.rowHeight=37;
const bf={10:'=MIN(MAX(B5,0),52*B4/12)',11:'=B2*B3*B10',12:'=B11/B4',13:'=B6/B4',14:'=B7/B4',15:'=B8/B4',16:'=SUM(B12:B15)',17:'=Summary!J26',18:'=B17+B9',19:'=IF(B16=0,"",B18/B16)',23:'=(B20+B21)/B22',24:'=IF(B16=0,"",B23/B16)',26:'=MIN(B11,B25)',27:'=B26/B4',28:'=IF(B2*B3=0,"",B25/(B2*B3))',31:'=B29/12',32:'=B30/12'};
for(const [r,f] of Object.entries(bf))formula(bs,'B'+r,f);
bs.getRange('B2:B32').setNumberFormat(money);for(const r of [3,4,5,10,22,28])bs.getRange('B'+r).setNumberFormat('0.00');for(const r of [19,24])bs.getRange('B'+r).setNumberFormat(percent);
for(const rangeName of ['B2:B9','B20:B22','B25'])bs.getRange(rangeName).format.fill='#FFF2CC';
bs.getRange('B4').dataValidation={rule:{type:'whole',operator:'between',formula1:1,formula2:12}};
bs.getRange('B22').dataValidation={rule:{type:'whole',operator:'between',formula1:1,formula2:20}};
for(const r of [2,3,5,6,7,8,9,20,21,25])bs.getRange('B'+r).dataValidation={rule:{type:'decimal',operator:'greaterThanOrEqual',formula1:0}};
// Official rate changes and academic-year conversions.
const hs=sheets['Housing rates'];
const rates=[['Residence hall double',3800,3970],['Residence hall single',4275,4600],['Wolf Village/Ridge 1 bedroom or studio',5000,5375],['Wolf Village/Ridge 2–4 bedrooms',4500,4780],['E.S. King undergraduate double',4125,4350],['E.S. King/Western Manor studio',3900,4150],['E.S. King/Western Manor 1 bedroom',4375,4600],['E.S. King/Western Manor 2 bedroom',5000,5300],['Coastal Quarters single',4225,4350],['Coastal Quarters double',3950,4025]];
block(hs,['Housing category','2025–26 $/semester','2026–27 projected $/semester','Dollar change','Percent change'],rates.map(r=>[...r,null,null]));hs.getRange('A:A').format.columnWidth=43;hs.getRange('B:D').format.columnWidth=25;hs.getRange('B2:D11').setNumberFormat(money);hs.getRange('E2:E11').setNumberFormat(percent);
for(let i=2;i<=11;i++){formula(hs,'D'+i,`=C${i}-B${i}`);formula(hs,'E'+i,`=D${i}/B${i}`);}
hs.getRange('A14:C19').values=[['Academic-year conversion','Value','Explanation'],['ResNet fee per semester',150,'Included in room examples; excluded from rate-change chart.'],['Semesters',2,'Fall + spring'],['Monthly-equivalent denominator',9,'Academic-year display convention; excludes summer'],['Double monthly equivalent',null,'(Projected room charge + ResNet) × semesters / months'],['Single monthly equivalent',null,'(Projected room charge + ResNet) × semesters / months']];formula(hs,'B18','= (C2+B15)*B16/B17');formula(hs,'B19','=(C3+B15)*B16/B17');hs.getRange('B18:B19').setNumberFormat(money);hs.getRange('C14:E20').format.wrapText=true;hs.getRange('A22:C23').values=[['Housing rate source','https://housing.dasa.ncsu.edu/residential-communities/costs/','2026–27 remains labeled projected'],['Budget source','https://studentservices.ncsu.edu/finances/estimated-cost-of-attendance/undergraduate-student-estimated-cost-of-attendance/','Fall + spring housing budgets: $8,738 on campus; $9,808 off campus.']];
// Guide makes caveats and source provenance visible without formulas hidden in prose.
const gs=sheets.Guide;
const guide=[
 ['Snapshot / revision',d.snapshot_date+' / '+d.review_date],['Analysis version',d.version],['Reading order','Summary → Listings → Raw properties / Raw floorplans. Use Budget for a separate personal scenario.'],
 ['Scope',d.scope],['Unit of observation','One portal listing ID. Not one building, tenant or available bedroom. Separate ads in a building may be related.'],
 ['Primary inclusion rule','Within five miles of any reference point; positive ordered price pair; no unresolved price basis or search/detail mismatch.'],
 ['Room overrides','23 whole-unit flags reclassified using 20 explicit saved room titles and 3 source descriptions. Snapshot prices unchanged.'],
 ['Source flags are not proof','Flags retained when no concrete contradiction was identified. Not every price or lease was independently verified.'],
 ['Price coverage','Advertised prices have varying fee coverage. Raw floorplans preserve separate all-in price ranges. Do not interpret as uniform all-in cost.'],
 ['Dates / lease terms','Future-only, waitlist, missing dates, sublets and different lease lengths remain in the primary advertised-offer sample.'],
 ['Sample limitations','Convenience sample of one portal. No claim of full-market coverage, statistical representativeness, available vacancies or student burden prevalence.'],
 ['Distance method','Haversine with Earth radius 3958.7613 miles; full-precision distances decide bands. Straight line, not route distance or campus-edge distance.'],
 ['Combined sample','Union by listing ID, not sum of campus counts. One ID appears once in the Listings table.'],
 ['Means','Sum low / included n; sum high / same n. Mean midpoint = (low mean + high mean) / 2. Do not average band means equally.'],
 ['Medians','Website also gives median individual midpoint as a robustness measure. Excel summary shows auditable endpoint and midpoint means.'],
 ['Original versus revised','Raw sheets are unchanged source values. Reviewed basis and basis-review flags are documented editorial inputs; numeric checks are formulas.'],
 ['Missing price','A raw zero or blank is preserved on source sheets; it fails the positive-pair test and does not lower the mean.'],
 ['Review flag meaning','1 means flagged; 0 means not flagged. Flags may overlap, so sum of reasons can exceed number of excluded IDs.'],
 ['Sensitivity','Omit future-only dates, waitlists and the flagged Centennial Ridge endpoint separately and together. Not an available-now sample.'],
 ['Budget input color','Pale yellow = editable scenario. Other cells are formulas or source/context. Loans are borrowed funds, not earnings.'],
 ['Aid year','CDS 2025–26 Section H selects 2024–25 Final. Different recipient-group means must not be treated as a typical combined package.'],
 ['HUD comparison','Housing plus utilities / household income is the HUD basis. This personal resources model is not a formal classification.'],
 ['Monthly periods','52/12 is a valid steady-work conversion, not a guarantee of year-round FWS. Enter actual weeks and months; FWS award cap example is separate.'],
 ['Source portal','https://offcampus.dasa.ncsu.edu/housing'],['Article / full methodology','https://strokeofluck.github.io/ncsu-rent-article/references.html'],
 ['Raw source commit',d.source_commit],['Property CSV SHA-256',d.raw_sha256['ncsu-properties.csv']],['Floor-plan CSV SHA-256',d.raw_sha256['ncsu-floorplans.csv']],
 ['Rebuild','python scripts/build_analysis.py; python scripts/prepare_workbook_sources.py; node scripts/build_workbook.mjs (requires @oai/artifact-tool).'],
 ['Updating raw data','Use a new dated snapshot and update the documented review decisions. This workbook is a fixed-snapshot audit; appended source rows require a rebuild.'],
 ['Financial aid source','https://report.isa.ncsu.edu/ir/cds/pdfs/CDS_2025-26.v1.pdf'],['Work-study source','https://emas.ncsu.edu/employment/federal-work-study-program/'],
 ['Aid allocation source','https://studentservices.ncsu.edu/finances/scholarships-and-financial-aid/receive-your-financial-aid/'],['HUD definitions','https://www.huduser.gov/portal/datasets/cp/CHAS/bg_chas.html']
];block(gs,['Audit guide','Definition / source'],guide);gs.getRange('A:A').format.columnWidth=29;gs.getRange('B:B').format.columnWidth=118;gs.getRange(`B2:B${guide.length+1}`).format.wrapText=true;gs.getRange(`A2:B${guide.length+1}`).format.rowHeight=42;
wb.recalculate();
// Calculated workbook outputs are verified against independently produced website arithmetic.
const expected=A.summarize(A.union(d.rentals));
const values=ss.getRange('D26:K27').values;
if(values[0][1]!==expected.perOverall.n||values[1][1]!==expected.wholeOverall.n||Math.abs(values[0][6]-expected.perOverall.midpoint)>1e-7||Math.abs(values[1][6]-expected.wholeOverall.midpoint)>1e-7) throw new Error('Workbook/site mismatch: '+JSON.stringify(values));
for(let i=0;i<d.rentals.length;i++){const r=d.rentals[i],v=ls.getRange(`L${i+2}:X${i+2}`).values[0];if(Boolean(v[3])!==r.eligible_price||Boolean(v[10])!==r.in_union||Math.abs(v[4]-r.distance_main)>1e-8||Math.abs(v[6]-r.distance_centennial)>1e-8||Math.abs(v[8]-r.distance_vet)>1e-8)throw new Error('Listing formula mismatch '+r.site_id);}
const budgetDefault=bs.getRange('B16:B19').values; if(Math.abs(budgetDefault[0][0]-1300)>1e-9||Math.abs(budgetDefault[3][0]-expected.perOverall.midpoint/1300)>1e-9)throw new Error('Budget formula mismatch');
// Meaningful recalc probes: tuition-net support, term work, and zero resources. Restore default before export.
bs.getRange('B4:B7').values=[[9],[30],[1800],[900]];wb.recalculate();if(Math.abs(bs.getRange('B16').values[0][0]-1300)>1e-8)throw new Error('Term aid recalc failed');
bs.getRange('B2').values=[[0]];bs.getRange('B6:B8').values=[[0],[0],[0]];wb.recalculate();if(bs.getRange('B19').values[0][0]!=='')throw new Error('Zero denominator not blank');
bs.getRange('B2').values=[[15]];bs.getRange('B4:B7').values=[[12],[52],[0],[0]];wb.recalculate();
console.log((await wb.inspect({kind:'region',sheetId:'Summary',range:'A24:K27',maxChars:4000,tableMaxRows:5,tableMaxCols:11})).ndjson);
for(const [name,r] of [['Guide','A1:B8'],['Raw properties','A1:F7'],['Raw floorplans','A1:H7'],['Listings','D1:O8'],['Summary','A1:K9'],['Sensitivity','A1:H11'],['Budget','A1:C19'],['Housing rates','A1:E11']]) {
 const preview=await wb.render({sheetName:name,range:r,scale:1,format:'png'});await fs.writeFile(path.join(qa,name.replaceAll(' ','-')+'.png'),new Uint8Array(await preview.arrayBuffer()));
}
await fs.writeFile(path.join(qa,'verification.json'),JSON.stringify({version:d.version,combined:values,budget:bs.getRange('B16:B19').values,allListingDistanceChecks:rows.length},null,2));
const xlsx=await SpreadsheetFile.exportXlsx(wb);await xlsx.save(path.join(out,'ncsu-rent-audit.xlsx'));
console.log('Exported '+path.join(out,'ncsu-rent-audit.xlsx'));
