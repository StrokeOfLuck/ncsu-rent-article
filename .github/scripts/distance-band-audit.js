const fs = require("fs");
const vm = require("vm");

function mustReplace(source, oldText, newText, label) {
  if (!source.includes(oldText)) throw new Error(`Missing ${label}`);
  return source.replace(oldText, newText);
}

function extractBalanced(source, marker, openChar, closeChar) {
  const markerPos = source.indexOf(marker);
  if (markerPos < 0) throw new Error(`Marker not found: ${marker}`);
  const start = source.indexOf(openChar, markerPos + marker.length);
  if (start < 0) throw new Error(`Opening ${openChar} not found after ${marker}`);
  let depth = 0, quote = null, escaped = false;
  for (let i = start; i < source.length; i++) {
    const ch = source[i];
    if (quote) {
      if (escaped) { escaped = false; continue; }
      if (ch === "\\") { escaped = true; continue; }
      if (ch === quote) quote = null;
      continue;
    }
    if (ch === '"' || ch === "'" || ch === "`") { quote = ch; continue; }
    if (ch === openChar) depth++;
    else if (ch === closeChar) {
      depth--;
      if (depth === 0) return source.slice(start, i + 1);
    }
  }
  throw new Error(`Unbalanced block after ${marker}`);
}

const bandFunction = `function getDistanceBandAudit(campusKey, innerRadius, outerRadius) {
  const c = campuses[campusKey];
  const band = rentals
    .map(p=>({...p, calculated_distance_miles:hav(c.lat,c.lon,p.lat,p.lon)}))
    .filter(p=>{
      const d = p.calculated_distance_miles;
      const aboveInner = innerRadius === 0 ? d >= 0 : d > innerRadius;
      return aboveInner && d <= outerRadius;
    })
    .sort((a,b)=>a.calculated_distance_miles-b.calculated_distance_miles);

  const per = band.filter(p=>p.pricing_type==="Per bedroom");
  const whole = band.filter(p=>p.pricing_type==="Whole unit");

  return {
    campus:c,
    innerRadius,
    outerRadius,
    near:band,
    perStats:averageStats(per),
    wholeStats:averageStats(whole)
  };
}

`;

const articleRender = `function renderSummaryTable() {
  const body = document.getElementById("summary");
  body.innerHTML = "";

  const bands = [
    {inner:0, outer:1, label:"0–1 mi"},
    {inner:1, outer:3, label:">1–3 mi"},
    {inner:3, outer:5, label:">3–5 mi"}
  ];

  for(const bandDef of bands) {
    const band = getDistanceBandAudit(currentCampusKey, bandDef.inner, bandDef.outer);
    const tr = document.createElement("tr");
    tr.innerHTML = ` + "`" + `
      <td>${bandDef.label}</td>
      <td>${band.near.length}</td>
      <td>${band.perStats.display}</td>
      <td>${band.wholeStats.display}</td>
    ` + "`" + `;
    body.appendChild(tr);
  }

  updateAffordability();
}`;

let index = fs.readFileSync("index.html", "utf8");
index = mustReplace(index, '<div class="section-label">Mean advertised rent by radius</div>', '<div class="section-label">Mean advertised rent by distance band</div>', "article distance-band heading");
index = mustReplace(index, '<th>Radius</th>\n          <th>Properties</th>\n          <th>Per bedroom</th>\n          <th>Whole unit</th>', '<th>Distance band</th>\n          <th>Properties</th>\n          <th>Per bedroom</th>\n          <th>Whole unit</th>', "article distance-band table header");
index = mustReplace(index, '<tbody id="summary"></tbody>\n    </table>', '<tbody id="summary"></tbody>\n    </table>\n    <div class="row-hint">Distance bands do not overlap: 0–1 mile, more than 1–3 miles, and more than 3–5 miles. Each listing appears in one band per campus.</div>', "article distance-band note");
if (!index.includes("function getDistanceBandAudit(")) index = mustReplace(index, "function getRadiusAudit(campusKey, radius) {", bandFunction + "function getRadiusAudit(campusKey, radius) {", "article band function insertion point");
const articleRenderRe = /function renderSummaryTable\(\) \{[\s\S]*?\n\}\n\nfunction formatIncomeCards/;
if (!articleRenderRe.test(index)) throw new Error("Article renderSummaryTable block not found");
index = index.replace(articleRenderRe, articleRender + "\n\nfunction formatIncomeCards");
index = index.replace('"Main, Centennial and Biomedical Campus · overall average of all displayed 1-, 3- and 5-mile summary ranges";', '"Main, Centennial and Biomedical Campus · all unique listings across the displayed 1-, 3- and 5-mile views, counted once";');
fs.writeFileSync("index.html", index);

let audit = fs.readFileSync("rental-map-audit.html", "utf8");
audit = mustReplace(audit, 'Advertised through NC State’s Off-Campus Housing site and collected Sept. 9, 2026; they are not the full Raleigh rental market. The overall affordability summary combines the Main, Centennial and Biomedical Campus 1-, 3- and 5-mile views. Campus boundaries and building footprints: NC State Facilities GIS. Distances are straight-line calculations from each campus reference point.', 'Advertised through NC State’s Off-Campus Housing site and collected Sept. 9, 2026; they are not the full Raleigh rental market. Campus boundaries and building footprints: NC State Facilities GIS. Distances are straight-line calculations from each campus reference point.', "audit footer note");

const oldAuditSection = `  <section class="block">
    <div class="section-label">Mean advertised rent by radius</div>
    <table>
      <thead>
        <tr>
          <th>Radius</th>
          <th>Properties</th>
          <th>Per bedroom</th>
          <th>Whole unit</th>
          <th>Audit</th>
        </tr>
      </thead>
      <tbody id="summary"></tbody>
    </table>
  </section>`;
const newAuditSection = `  <section class="block">
    <div class="section-label">Cumulative radius audit</div>
    <div class="row-hint"><strong>These rows overlap.</strong> ≤ 3 miles includes the listings already counted within ≤ 1 mile, and ≤ 5 miles includes the listings already counted within both smaller radii.</div>
    <table>
      <thead><tr><th>Radius</th><th>Properties</th><th>Per bedroom</th><th>Whole unit</th><th>Audit</th></tr></thead>
      <tbody id="summary"></tbody>
    </table>
    <div class="section-label" style="margin-top:20px;">Non-overlapping distance bands</div>
    <div class="row-hint">Use these bands to compare rent by distance. Each listing appears in only one band for the selected campus.</div>
    <table>
      <thead><tr><th>Distance band</th><th>Properties</th><th>Per bedroom</th><th>Whole unit</th><th>Audit</th></tr></thead>
      <tbody id="bandSummary"></tbody>
    </table>
  </section>`;
audit = mustReplace(audit, oldAuditSection, newAuditSection, "audit tables section");
if (!audit.includes("function getDistanceBandAudit(")) audit = mustReplace(audit, "function getRadiusAudit(campusKey, radius) {", bandFunction + "function getRadiusAudit(campusKey, radius) {", "audit band function insertion point");

const newDownload = `function downloadRadiusXLSX(radius) {
  const audit = getRadiusAudit(currentCampusKey, radius);
  const c = audit.campus;
  const innerRadius = radius === 1 ? 0 : radius === 3 ? 1 : radius === 5 ? 3 : 0;
  const band = getDistanceBandAudit(currentCampusKey, innerRadius, radius);
  const bandLabel = innerRadius === 0 ? ` + "`" + `0–${radius} mi` + "`" + ` : ` + "`" + `>${innerRadius}–${radius} mi` + "`" + `;

  function baseRow(p) {
    return {site_id:p.site_id, ocp_id:p.ocp_id, property_name:p.name, street_address:p.address, city:p.city, state:p.state, zip:p.zip, latitude:p.lat, longitude:p.lon, distance_from_reference_miles:Number(p.calculated_distance_miles.toFixed(6)), pricing_type:p.pricing_type, rent_low:p.rent_low, rent_high:p.rent_high, advertised_rent:p.rent_display, beds:p.beds_display, shared_space:p.shared_space, sublet:p.sublet, lease_term:p.lease_term, property_type:p.property_type, original_ncsu_listing:p.listing_url};
  }

  const cumulativeRows = audit.near.map(p=>({selected_campus:c.label, campus_reference_latitude:c.lat, campus_reference_longitude:c.lon, scope_type:"CUMULATIVE / OVERLAPPING", radius_scope:` + "`" + `0–${radius} miles (≤ ${radius} mi)` + "`" + `, overlap_note:"Cumulative radius. Listings inside smaller radii are included again in larger-radius rows.", total_properties_in_scope:audit.near.length, ...baseRow(p)}));
  const bandRows = band.near.map(p=>({selected_campus:c.label, campus_reference_latitude:c.lat, campus_reference_longitude:c.lon, scope_type:"NON-OVERLAPPING DISTANCE BAND", distance_band:bandLabel, boundary_rule:innerRadius === 0 ? ` + "`" + `0 ≤ distance ≤ ${radius} mile` + "`" + ` : ` + "`" + `${innerRadius} < distance ≤ ${radius} miles` + "`" + `, total_properties_in_band:band.near.length, ...baseRow(p)}));

  function cleanRows(rows, pricingType, scopeLabel) {
    return rows.filter(p=>p.pricing_type===pricingType).map(p=>({scope:scopeLabel, property_name:p.property_name, street_address:p.street_address, city:p.city, distance_from_reference_miles:p.distance_from_reference_miles, rent_low:p.rent_low, rent_high:p.rent_high, advertised_rent:p.advertised_rent, beds:p.beds, lease_term:p.lease_term, property_type:p.property_type, shared_space:p.shared_space, sublet:p.sublet, original_ncsu_listing:p.original_ncsu_listing}));
  }

  function addCalcBlock(ws, rows, scopeNote) {
    if (!rows.length) { XLSX.utils.sheet_add_aoa(ws, [["SCOPE NOTE", scopeNote], ["No listings in this scope."]], {origin:"A1"}); return; }
    const headers = Object.keys(rows[0]);
    const pricingCol = XLSX.utils.encode_col(headers.indexOf("pricing_type"));
    const lowCol = XLSX.utils.encode_col(headers.indexOf("rent_low"));
    const highCol = XLSX.utils.encode_col(headers.indexOf("rent_high"));
    const last = rows.length + 1, start = last + 3;
    XLSX.utils.sheet_add_aoa(ws, [
      ["CALCULATION CHECK","Rent low","Rent high"],
      ["Per bedroom SUM", {f:` + "`" + `SUMIF($${pricingCol}$2:$${pricingCol}$${last},"Per bedroom",$${lowCol}$2:$${lowCol}$${last})` + "`" + `}, {f:` + "`" + `SUMIF($${pricingCol}$2:$${pricingCol}$${last},"Per bedroom",$${highCol}$2:$${highCol}$${last})` + "`" + `}],
      ["Per bedroom COUNT", {f:` + "`" + `COUNTIFS($${pricingCol}$2:$${pricingCol}$${last},"Per bedroom",$${lowCol}$2:$${lowCol}$${last},">0")` + "`" + `}, {f:` + "`" + `COUNTIFS($${pricingCol}$2:$${pricingCol}$${last},"Per bedroom",$${highCol}$2:$${highCol}$${last},">0")` + "`" + `}],
      ["Per bedroom AVERAGE", {f:` + "`" + `ROUND(AVERAGEIF($${pricingCol}$2:$${pricingCol}$${last},"Per bedroom",$${lowCol}$2:$${lowCol}$${last}),2)` + "`" + `}, {f:` + "`" + `ROUND(AVERAGEIF($${pricingCol}$2:$${pricingCol}$${last},"Per bedroom",$${highCol}$2:$${highCol}$${last}),2)` + "`" + `}],
      [],
      ["Whole unit SUM", {f:` + "`" + `SUMIF($${pricingCol}$2:$${pricingCol}$${last},"Whole unit",$${lowCol}$2:$${lowCol}$${last})` + "`" + `}, {f:` + "`" + `SUMIF($${pricingCol}$2:$${pricingCol}$${last},"Whole unit",$${highCol}$2:$${highCol}$${last})` + "`" + `}],
      ["Whole unit COUNT", {f:` + "`" + `COUNTIFS($${pricingCol}$2:$${pricingCol}$${last},"Whole unit",$${lowCol}$2:$${lowCol}$${last},">0")` + "`" + `}, {f:` + "`" + `COUNTIFS($${pricingCol}$2:$${pricingCol}$${last},"Whole unit",$${highCol}$2:$${highCol}$${last},">0")` + "`" + `}],
      ["Whole unit AVERAGE", {f:` + "`" + `ROUND(AVERAGEIF($${pricingCol}$2:$${pricingCol}$${last},"Whole unit",$${lowCol}$2:$${lowCol}$${last}),2)` + "`" + `}, {f:` + "`" + `ROUND(AVERAGEIF($${pricingCol}$2:$${pricingCol}$${last},"Whole unit",$${highCol}$2:$${highCol}$${last}),2)` + "`" + `}],
      [], ["SCOPE NOTE", scopeNote], ["DISTANCE METHOD", "Straight-line Haversine distance from the selected campus reference point."]
    ], {origin:` + "`" + `A${start}` + "`" + `});
    ws["!autofilter"] = {ref:` + "`" + `A1:${XLSX.utils.encode_col(headers.length - 1)}${last}` + "`" + `}; ws["!freeze"] = {xSplit:0,ySplit:1};
  }

  function addCleanCalcBlock(ws, rows, label, scopeNote) {
    if (!rows.length) { XLSX.utils.sheet_add_aoa(ws, [["SCOPE NOTE", scopeNote], ["No listings in this pricing group."]], {origin:"A1"}); return; }
    const first = 2, last = rows.length + 1, start = last + 3;
    XLSX.utils.sheet_add_aoa(ws, [["CALCULATION CHECK","Rent low","Rent high"], [` + "`" + `${label} SUM` + "`" + `,{f:` + "`" + `SUM(F${first}:F${last})` + "`" + `},{f:` + "`" + `SUM(G${first}:G${last})` + "`" + `}], [` + "`" + `${label} COUNT` + "`" + `,{f:` + "`" + `COUNT(F${first}:F${last})` + "`" + `},{f:` + "`" + `COUNT(G${first}:G${last})` + "`" + `}], [` + "`" + `${label} AVERAGE` + "`" + `,{f:` + "`" + `ROUND(AVERAGE(F${first}:F${last}),2)` + "`" + `},{f:` + "`" + `ROUND(AVERAGE(G${first}:G${last}),2)` + "`" + `}], [], ["SCOPE NOTE",scopeNote]], {origin:` + "`" + `A${start}` + "`" + `});
    ws["!autofilter"] = {ref:` + "`" + `A1:M${last}` + "`" + `}; ws["!freeze"] = {xSplit:0,ySplit:1};
  }

  const wb = XLSX.utils.book_new();
  const wsAudit = XLSX.utils.json_to_sheet(cumulativeRows); addCalcBlock(wsAudit, cumulativeRows, ` + "`" + `CUMULATIVE / OVERLAPPING: all listings with distance ≤ ${radius} miles. Larger cumulative radii repeat listings from smaller radii.` + "`" + `); XLSX.utils.book_append_sheet(wb, wsAudit, "Cumulative Audit");
  const cumulativePer = cleanRows(cumulativeRows, "Per bedroom", ` + "`" + `≤ ${radius} mi cumulative` + "`" + `); const wsPer = XLSX.utils.json_to_sheet(cumulativePer); addCleanCalcBlock(wsPer, cumulativePer, "Per bedroom", ` + "`" + `CUMULATIVE / OVERLAPPING ≤ ${radius} mi.` + "`" + `); XLSX.utils.book_append_sheet(wb, wsPer, "Cumulative Per Bed");
  const cumulativeWhole = cleanRows(cumulativeRows, "Whole unit", ` + "`" + `≤ ${radius} mi cumulative` + "`" + `); const wsWhole = XLSX.utils.json_to_sheet(cumulativeWhole); addCleanCalcBlock(wsWhole, cumulativeWhole, "Whole unit", ` + "`" + `CUMULATIVE / OVERLAPPING ≤ ${radius} mi.` + "`" + `); XLSX.utils.book_append_sheet(wb, wsWhole, "Cumulative Whole Unit");
  const wsBand = XLSX.utils.json_to_sheet(bandRows); addCalcBlock(wsBand, bandRows, ` + "`" + `NON-OVERLAPPING DISTANCE BAND: ${bandLabel}. This is the confined territory used for the article's distance-band comparison.` + "`" + `); XLSX.utils.book_append_sheet(wb, wsBand, "Distance Band");

  const shortName = currentCampusKey==="main" ? "main-campus" : currentCampusKey==="centennial" ? "centennial-campus" : "biomedical-campus";
  XLSX.writeFile(wb, ` + "`" + `ncsu-rent-audit_${shortName}_${radius}mi.xlsx` + "`" + `, {compression:true});
}`;
const downloadRe = /function downloadRadiusXLSX\(radius\) \{[\s\S]*?\n\}\n\nfunction circlePolygon/;
if (!downloadRe.test(audit)) throw new Error("Audit downloadRadiusXLSX block not found");
audit = audit.replace(downloadRe, newDownload + "\n\nfunction circlePolygon");

const auditRender = `function renderSummaryTable() {
  const body = document.getElementById("summary");
  const bandBody = document.getElementById("bandSummary");
  body.innerHTML = ""; bandBody.innerHTML = "";
  for(const r of radii) {
    const audit = getRadiusAudit(currentCampusKey, r);
    const tr = document.createElement("tr"); tr.dataset.radius = r;
    tr.innerHTML = ` + "`" + `<td>≤ ${r} mi</td><td>${audit.near.length}</td><td>${audit.perStats.display}</td><td>${audit.wholeStats.display}</td><td><button class="audit-btn" onclick="downloadRadiusXLSX(${r})">XLSX</button></td>` + "`" + `;
    body.appendChild(tr);
  }
  const bands = [{inner:0,outer:1,label:"0–1 mi"},{inner:1,outer:3,label:">1–3 mi"},{inner:3,outer:5,label:">3–5 mi"}];
  for(const bandDef of bands) {
    const band = getDistanceBandAudit(currentCampusKey, bandDef.inner, bandDef.outer);
    const tr = document.createElement("tr");
    tr.innerHTML = ` + "`" + `<td>${bandDef.label}</td><td>${band.near.length}</td><td>${band.perStats.display}</td><td>${band.wholeStats.display}</td><td><button class="audit-btn" onclick="downloadRadiusXLSX(${bandDef.outer})">XLSX</button></td>` + "`" + `;
    bandBody.appendChild(tr);
  }
  updateAffordability();
}`;
const auditRenderRe = /function renderSummaryTable\(\) \{[\s\S]*?\n\}\n\nfunction formatIncomeCards/;
if (!auditRenderRe.test(audit)) throw new Error("Audit renderSummaryTable block not found");
audit = audit.replace(auditRenderRe, auditRender + "\n\nfunction formatIncomeCards");
fs.writeFileSync("rental-map-audit.html", audit);

const rentals = JSON.parse(extractBalanced(index, "const rentals =", "[", "]"));
const campuses = vm.runInNewContext("(" + extractBalanced(index, "const campuses =", "{", "}") + ")");
function hav(lat1, lon1, lat2, lon2) { const R=3958.7613, rad=x=>x*Math.PI/180; const p1=rad(lat1),p2=rad(lat2),dp=rad(lat2-lat1),dl=rad(lon2-lon1); const a=Math.sin(dp/2)**2+Math.cos(p1)*Math.cos(p2)*Math.sin(dl/2)**2; return 2*R*Math.asin(Math.sqrt(a)); }
function sumStats(rows,type,field){ const vals=rows.filter(r=>r.pricing_type===type).map(r=>r[field]).filter(v=>v!=null&&Number.isFinite(Number(v))).map(Number); const sum=vals.reduce((a,b)=>a+b,0); return {n:vals.length,sum,avg:vals.length?sum/vals.length:null}; }
function h(s){return String(s).replaceAll("&","&amp;").replaceAll("<","&lt;").replaceAll(">","&gt;");}
function money2(v){return v==null?"—":"$"+v.toLocaleString("en-US",{minimumFractionDigits:2,maximumFractionDigits:2});}
function mathCell(rows,type,field){const s=sumStats(rows,type,field);return !s.n?"—":`${money2(s.sum)} ÷ ${s.n} = <strong>${money2(s.avg)}</strong>`;}
const defs=[{inner:0,outer:1,label:"0–1 mi"},{inner:1,outer:3,label:">1–3 mi"},{inner:3,outer:5,label:">3–5 mi"}];
let rowsHtml="";
for(const key of ["main","centennial","vet"]){const c=campuses[key];for(const d of defs){const rows=rentals.map(r=>({...r,_d:hav(c.lat,c.lon,r.lat,r.lon)})).filter(r=>(d.inner===0?r._d>=0:r._d>d.inner)&&r._d<=d.outer);rowsHtml+=`\n<tr><td>${h(c.label)}</td><td>${d.label}</td><td>${rows.length}</td><td>${mathCell(rows,"Per bedroom","rent_low")}</td><td>${mathCell(rows,"Per bedroom","rent_high")}</td><td>${mathCell(rows,"Whole unit","rent_low")}</td><td>${mathCell(rows,"Whole unit","rent_high")}</td></tr>`;}}
const bandMathHtml=`
        <div class="use-note distance-band-method"><strong>Non-overlapping distance-band method:</strong> The article's distance comparison uses <strong>0–1 mile</strong>, <strong>more than 1–3 miles</strong>, and <strong>more than 3–5 miles</strong> from the selected campus reference point. A listing can appear in only one band within a campus comparison. Distances are straight-line Haversine calculations from the campus reference point. The rent figures in each cell are calculated directly from the listings in that band, not by subtracting or averaging the cumulative-radius averages.</div>
        <div class="band-math-wrap"><table class="band-math-table" aria-label="Worked rent calculations for non-overlapping campus distance bands"><thead><tr><th>Campus</th><th>Distance band</th><th>Properties</th><th>Per bedroom low: sum ÷ n = mean</th><th>Per bedroom high: sum ÷ n = mean</th><th>Whole unit low: sum ÷ n = mean</th><th>Whole unit high: sum ÷ n = mean</th></tr></thead><tbody>${rowsHtml}</tbody></table></div>
        <div class="filter-note"><strong>Cumulative-radius audit:</strong> The audit page also preserves the original <strong>≤ 1, ≤ 3 and ≤ 5 mile</strong> views. Those rows intentionally overlap: ≤ 3 miles repeats the ≤ 1-mile listings, and ≤ 5 miles repeats listings from both smaller radii. Each XLSX now labels the cumulative sheets as overlapping and includes a <strong>Distance Band</strong> tab containing every listing in the matching non-overlapping territory, its calculated distance from the campus reference point, and spreadsheet SUM, COUNT and AVERAGE checks.</div>`;

let refs=fs.readFileSync("references.html","utf8");
if(!refs.includes(".band-math-wrap")) refs=refs.replace("</style>",`.band-math-wrap{margin-top:10px;overflow-x:auto;border:1px solid var(--line)}.band-math-table{min-width:1180px;width:100%;border-collapse:collapse;font-size:10px;font-variant-numeric:tabular-nums}.band-math-table th,.band-math-table td{padding:8px 9px;border-bottom:1px solid #ece8e1;text-align:left;vertical-align:top;white-space:nowrap}.band-math-table th{background:var(--soft);color:var(--muted);font-size:8.5px;text-transform:uppercase;letter-spacing:.05em}.band-math-table td:nth-child(1),.band-math-table td:nth-child(2){font-weight:700}.distance-band-method{margin-top:12px}\n</style>`);
const anchor=/(<div class="use-note">\s*<strong>Worked calculation for the combined rent summary:<\/strong>[\s\S]*?<strong>Why this is the combined set:<\/strong>[\s\S]*?<\/div>)/;
if(!refs.includes("Worked rent calculations for non-overlapping campus distance bands")){if(!anchor.test(refs))throw new Error("Combined summary worked-calculation anchor not found");refs=refs.replace(anchor,"$1\n"+bandMathHtml);}
refs=refs.replace("Dedicated reporting copy of the rental map and mean-rent-by-radius table, with the XLSX audit controls preserved outside the reader-facing article.","Dedicated reporting copy of the rental map with both cumulative-radius and non-overlapping distance-band rent tables, with XLSX audit controls preserved outside the reader-facing article.");
refs=refs.replace("Each 1-, 3- and 5-mile row includes an XLSX button for reviewing the records and calculations behind that campus-radius summary.","Each cumulative 1-, 3- and 5-mile row includes an XLSX button. The workbook labels the cumulative sheets as overlapping and adds a Distance Band tab for the matching 0–1, >1–3 or >3–5 mile territory, including every row, calculated distance from the campus reference point, and formula checks.");
fs.writeFileSync("references.html",refs);

let readme=fs.readFileSync("README.md","utf8");
readme=readme.replace("- an XLSX audit download for each radius with three tabs: Full Audit, Per Bedroom and Whole Unit","- an XLSX audit download for each cumulative radius with clearly labeled overlapping cumulative sheets plus a non-overlapping Distance Band tab containing row-level distances and calculation checks");
fs.writeFileSync("README.md",readme);
