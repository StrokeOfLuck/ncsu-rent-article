/** Author the downloadable audit with @oai/artifact-tool. Source CSVs remain intact. */
import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { Workbook, SpreadsheetFile } from '@oai/artifact-tool';
const root=path.resolve(process.argv[2]||path.dirname(path.dirname(fileURLToPath(import.meta.url))));
const {default:A}=await import(pathToFileURL(path.join(root,'assets/rent-analysis.js')).href);
const d=JSON.parse(await fs.readFile(path.join(root,'data/reviewed-rentals.json'),'utf8'));
const raw=JSON.parse(await fs.readFile(path.join(root,'data/audits/source-tables.json'),'utf8'));
const out=process.env.RENT_AUDIT_OUTPUT_DIR||path.join(root,'data/audits'), qa=process.env.RENT_AUDIT_QA_DIR||'/tmp/ncsu-rent-workbook-qa';
await fs.mkdir(out,{recursive:true});
await fs.mkdir(qa,{recursive:true});
const wb=Workbook.create();
const bandDefs=Object.keys(d.campuses).flatMap(key=>[[0,1,'0-1 mi'],[1,3,'1-3 mi'],[3,5,'3-5 mi']].map(([low,high,label])=>({key,low,high,name:({main:'Main',centennial:'Centennial',vet:'Biomedical'}[key])+' '+label})));
const names=['Summary','Rooms',...bandDefs.map(b=>b.name),'Excluded','Listings','Raw properties','Raw floorplans'];
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
 sh.tables.add(`A1:${col(headers.length-1)}${rs.length+1}`,true,sheet==='Raw properties'?'RawProperties':'RawFloorplans').showFilterButton=true;
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

// These are dated, ID-keyed extracts. Rebuild when inclusion decisions change.
const roomRows=d.rentals.filter(r=>r.in_union&&A.valid(r)&&r.pricing_type==='Per bedroom').sort((a,b)=>a.name.localeCompare(b.name,'en'));
const excluded=d.rentals.filter(r=>!roomRows.some(x=>x.site_id===r.site_id)).sort((a,b)=>a.name.localeCompare(b.name,'en'));
const totals={};
function linked(sh,target,source,idCell){
 const v=`INDEX('Listings'!$${source}$2:$${source}$${end},MATCH(${idCell},'Listings'!$A$2:$A$${end},0))`;
 formula(sh,target,`=IF(${v}="","",${v})`);
}
function roomTab(name,rs,key){
 const sh=sheets[name],last=rs.length+5;
 sh.getRange(`A1:K${last+10}`).format.font={name:'Arial',size:10};sh.showGridLines=false;
 sh.getRange('A2').values=[[name==='Rooms'?'All room listings':name.replace('1-3','>1–3').replace('3-5','>3–5').replace('0-1','0–1')]];
 sh.getRange('A2').format.font={bold:true,size:14};
 sh.getRange('A3').values=[['September 9, 2026 snapshot. Totals use every listed row, including filtered-out rows.']];
 const hs=['Listing name','Low ($/month)','High ($/month)','Midpoint ($/month)',key?'Distance (mi)':'Main distance (mi)','Listing ID','Source URL'];
 if(!key)hs.push('Centennial distance (mi)','Biomedical distance (mi)');
 const lastcol=col(hs.length-1);
 sh.getRange(`A5:${lastcol}5`).values=[hs];
 sh.getRange(`A5:${lastcol}5`).format={fill:'#2D485D',font:{bold:true,color:'#FFFFFF'},wrapText:true,rowHeight:32,horizontalAlignment:'center'};
 for(let j=0;j<rs.length;j++){
  const i=j+6;sh.getRange('F'+i).values=[[rs[j].site_id]];
  for(const [to,from] of [['A','B'],['B','H'],['C','I'],['G','C'],['E',key?{main:'P',centennial:'R',vet:'T'}[key]:'P'],...(!key?[['H','R'],['I','T']]:[])])linked(sh,to+i,from,'$F'+i);
  formula(sh,'D'+i,`=(B${i}+C${i})/2`);
 }
 sh.getRange('A:A').format.columnWidth=44;sh.getRange('B:D').format.columnWidth=18;sh.getRange('E:F').format.columnWidth=18;sh.getRange('G:G').format.columnWidth=44;
 if(!key){sh.getRange('H:I').format.columnWidth=20;sh.getRange(`H6:I${last}`).setNumberFormat('0.000000');}
 sh.getRange(`A6:${lastcol}${last}`).format.rowHeight=32;sh.getRange(`A6:A${last}`).format.wrapText=true;
 sh.getRange(`E6:E${last}`).setNumberFormat('0.000000');sh.getRange(`B6:D${last+7}`).setNumberFormat(money);
 sh.freezePanes.freezeRows(5);sh.tables.add(`A5:${lastcol}${last}`,true,name.replace(/[^A-Za-z0-9]/g,'')+'Prices').showFilterButton=true;
 const count=last+2,sum=last+3,mean=last+4,median=last+5;
 sh.getRange(`A${count}:A${median}`).values=[['Prices used (COUNT)'],['Total advertised rent (SUM)'],['Average (sum / count)'],['Median listing midpoint']];
 for(const c of ['B','C','D']){
  formula(sh,c+count,`=COUNT(${c}6:${c}${last})`);formula(sh,c+sum,`=SUM(${c}6:${c}${last})`);formula(sh,c+mean,`=${c}${sum}/${c}${count}`);
 }
 formula(sh,'D'+median,`=MEDIAN(D6:D${last})`);
 sh.getRange(`B${count}:D${count}`).setNumberFormat('0');
 sh.getRange(`A${sum}:D${mean}`).format.font={bold:true};sh.getRange(`A${mean}:D${mean}`).format.fill='#E8EEF2';
 sh.getRange(`A${count}:D${median}`).format.rowHeight=24;
 sh.getRange('A'+(median+2)).values=[['Each listing has equal weight. Distance uses unrounded straight-line miles.']];
 sh.getRange('A'+(median+3)).values=[['Price ranges are average low to average high, not confidence intervals.']];
 totals[name]={count,sum,mean,median,last,ids:rs.map(r=>r.site_id)};
}
roomTab('Rooms',roomRows);
for(const b of bandDefs)roomTab(b.name,roomRows.filter(r=>r['distance_'+b.key]<=b.high&&(b.low===0||r['distance_'+b.key]>b.low)),b.key);
function exclusionReason(r){
 const reasons=[];
 if(!r.in_union)reasons.push('Outside all three five-mile areas');
 if(r.pricing_type==='Whole unit')reasons.push('Whole-unit offer, outside room-only scope');
 else if(r.pricing_type!=='Per bedroom')reasons.push('Not a resolved room/per-bedroom offer');
 if(!A.valid(r))reasons.push(r.exclusion_reason||r.review_status);
 return reasons.join('. ')+'.';
}
block(sheets.Excluded,['Listing name','Reviewed basis','Reason excluded from room article','Listing ID','Source URL','Review evidence'],excluded.map(r=>[r.name,r.pricing_type,exclusionReason(r),r.site_id,r.listing_url,r.review_note]));
const ex=sheets.Excluded;ex.getRange('A:A').format.columnWidth=40;ex.getRange('B:B').format.columnWidth=20;ex.getRange('C:C').format.columnWidth=64;ex.getRange('D:E').format.columnWidth=24;ex.getRange('F:F').format.columnWidth=80;
ex.getRange(`A2:F${excluded.length+1}`).format.wrapText=true;ex.getRange(`A2:F${excluded.length+1}`).format.autofitRows();ex.tables.add(`A1:F${excluded.length+1}`,true,'RoomExclusions').showFilterButton=true;
const ss=sheets.Summary;ss.showGridLines=false;ss.tabColor='#2D485D';ss.getRange('A1:G42').format.font={name:'Arial',size:10};ss.getRange('A:A').format.columnWidth=34;ss.getRange('B:G').format.columnWidth=19;
ss.getRange('A2').values=[['Room rent audit']];ss.getRange('A2').format.font={bold:true,size:14};ss.getRange('A3').values=[['September 9, 2026 advertised-price snapshot. Classifications reviewed September 13.']];
ss.getRange('A5:G5').values=[['Campus / distance','Room listings','Low-price sum','High-price sum','Average low','Average high','Mean midpoint']];ss.getRange('A5:G5').format={fill:'#2D485D',font:{bold:true,color:'#FFFFFF'},wrapText:true,rowHeight:32,horizontalAlignment:'center'};
const summaryItems=[];
for(const [key,c] of Object.entries(d.campuses)){
 const own=bandDefs.filter(b=>b.key===key),start=summaryItems.length+6;
 for(const b of own)summaryItems.push({name:b.name,tab:b.name});
 summaryItems.push({name:(key==='vet'?'Biomedical':c.label)+' total',start,end:start+2});
}
summaryItems.push({name:'All three areas, unique IDs',tab:'Rooms'});
for(let j=0;j<summaryItems.length;j++){
 const i=j+6,item=summaryItems[j];ss.getRange('A'+i).values=[[item.name]];
 if(item.tab){const t=totals[item.tab];for(const [dest,source,row] of [['B','B',t.count],['C','B',t.sum],['D','C',t.sum],['E','B',t.mean],['F','C',t.mean],['G','D',t.mean]])formula(ss,dest+i,`='${item.tab}'!${source}${row}`);}
 else{for(const c of ['B','C','D'])formula(ss,c+i,`=SUM(${c}${item.start}:${c}${item.end})`);formula(ss,'E'+i,`=C${i}/B${i}`);formula(ss,'F'+i,`=D${i}/B${i}`);formula(ss,'G'+i,`=(E${i}+F${i})/2`);ss.getRange(`A${i}:G${i}`).format.fill='#E8EEF2';ss.getRange(`A${i}:G${i}`).format.font={bold:true};}
}
ss.getRange('C6:G18').setNumberFormat(money);ss.getRange('A6:G18').format.rowHeight=25;
const notes=[
 ['Read the math','Open a distance-band tab and scroll below its listings. COUNT, SUM, average and median are live Excel formulas.'],
 ['Main Campus count','18 + 46 + 10 = 74 article listings after the Sept. 20 bedroom-occupancy review.'],
 ['Overlapping campuses','Do not add campus totals. Rooms has 76 unique IDs across the union of the three campus areas after the two occupancy exclusions.'],
 ['Raw to reviewed to rooms','Raw properties and Raw floorplans preserve the saved source values. Listings applies reviewed categories and formula checks. Rooms keeps usable room offers within five miles of any campus.'],
 ['Excluded scope','Excluded has 92 IDs not used in the room article, including the explicitly shared-bedroom and occupancy-unclear listings. Valid whole-unit offers are outside this scope, not bad data. Reasons can overlap. Rooms plus Excluded account for all 168 raw IDs.'],
 ['Updating this audit','These are fixed, ID-keyed extracts. Source-linked values and formulas recalculate. Rebuild after changing membership, locations, categories or adding source rows. Filters do not change the published totals.'],
 ['Advertised offers','Includes future move-ins, waitlist mentions and varied lease lengths. It is not a count of vacancies available now. Live listings may have changed.'],
 ['What the mean measures','One contribution per listing ID. Not weighted by bedrooms, available units, student demand or closeness. Small groups deserve caution, especially Biomedical 0–1 mile (4 offers).'],
 ['Price coverage','Monthly advertised low and high prices may omit utilities and fees. Each midpoint = (low + high) / 2. Keep full precision and round only displayed results.'],
 ['Sensitivity and budget','The complete audit workbook retains future-only, waitlist and high-endpoint sensitivity checks, aid assumptions and personal-budget calculations.'],
 ['Source portal','https://offcampus.dasa.ncsu.edu/housing'],
 ['Methods and other audit','https://strokeofluck.github.io/ncsu-rent-article/references.html#audit-downloads'],
 ['Source property SHA-256',d.raw_sha256['ncsu-properties.csv']],
 ['Source floorplans SHA-256',d.raw_sha256['ncsu-floorplans.csv']]
];
for(let j=0;j<notes.length;j++){const i=j+21;ss.getRange('A'+i).values=[[notes[j][0]]];ss.mergeCells(`B${i}:G${i}`);ss.getRange('B'+i).values=[[notes[j][1]]];ss.getRange(`A${i}:G${i}`).format.wrapText=true;ss.getRange(`A${i}:G${i}`).format.rowHeight=j===3||j===5?42:32;}
wb.recalculate();
for(const [name,t] of Object.entries(totals)){
 const rs=d.rentals.filter(r=>t.ids.includes(r.site_id)),expected=A.stats(rs),v=sheets[name].getRange(`B${t.count}:D${t.mean}`).values;
 if(v[0].some(x=>x!==rs.length)||Math.abs(v[1][0]-expected.low_sum)>1e-7||Math.abs(v[1][1]-expected.high_sum)>1e-7||Math.abs(v[2][2]-expected.midpoint)>1e-7)throw Error('Room tab arithmetic mismatch: '+name);
}
if(roomRows.length!==76||excluded.length!==92||new Set([...roomRows,...excluded].map(r=>r.site_id)).size!==168)throw Error('Room/excluded partition');
for(let j=0;j<d.rentals.length;j++){
 const r=d.rentals[j],v=ls.getRange(`O${j+2}:U${j+2}`).values[0];
 if(v[0]!==+r.eligible_price||Math.abs(v[1]-r.distance_main)>1e-8||Math.abs(v[3]-r.distance_centennial)>1e-8||Math.abs(v[5]-r.distance_vet)>1e-8)throw Error('Source calculation mismatch: '+r.site_id);
}
// Verify a source price change reaches the extracted row and its mean, then restore.
const probe=roomRows.find(r=>r.distance_main<=1),rawIndex=raw.properties.findIndex(r=>r.site_id===probe.site_id)+2,original=Number(raw.properties[rawIndex-2].rent_low),rt=totals['Main 0-1 mi'];
const oldMean=sheets['Main 0-1 mi'].getRange('B'+rt.mean).values[0][0];sheets['Raw properties'].getRange(rawCol('rent_low')+rawIndex).values=[[original+20]];wb.recalculate();
if(Math.abs(sheets['Main 0-1 mi'].getRange('B'+rt.mean).values[0][0]-oldMean-20/rt.ids.length)>1e-7)throw Error('Source-to-band recalculation failed');
sheets['Raw properties'].getRange(rawCol('rent_low')+rawIndex).values=[[original]];wb.recalculate();
console.log((await wb.inspect({kind:'region',sheetId:'Summary',range:'A6:G18',maxChars:2200,tableMaxRows:13,tableMaxCols:7})).ndjson);
console.log((await wb.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!|#SPILL!|#CALC!',options:{useRegex:true,maxResults:10},maxChars:1200})).ndjson);
for(const name of names){
 const t=totals[name],ranges=t?[['top','A2:F9'],['math',`A${t.count}:D${t.median}`]]:[['top',name==='Summary'?'A2:G18':name==='Excluded'?'A1:D6':name==='Listings'?'A1:E5':name==='Raw properties'?'A1:E5':'A1:F5']];
 for(const [kind,range] of ranges){const blob=await wb.render({sheetName:name,range,scale:1,format:'png'});await fs.writeFile(path.join(qa,name.replaceAll(' ','_')+'-'+kind+'.png'),new Uint8Array(await blob.arrayBuffer()));}
}
await fs.writeFile(path.join(qa,'room-totals.json'),JSON.stringify(totals,null,2));
const xlsx=await SpreadsheetFile.exportXlsx(wb);await xlsx.save(path.join(out,'ncsu-room-rent-audit.xlsx'));
console.log('Exported room audit: '+roomRows.length+' kept, '+excluded.length+' excluded, '+bandDefs.length+' band tabs.');
