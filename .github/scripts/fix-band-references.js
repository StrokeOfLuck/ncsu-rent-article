const fs = require("fs");
const vm = require("vm");

function extractBalanced(source, marker, openChar, closeChar) {
  const markerPos = source.indexOf(marker);
  if (markerPos < 0) throw new Error("Marker not found: " + marker);
  const start = source.indexOf(openChar, markerPos + marker.length);
  if (start < 0) throw new Error("Opening character not found after " + marker);
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
  throw new Error("Unbalanced block after " + marker);
}

function hav(lat1, lon1, lat2, lon2) {
  const R = 3958.7613, rad = x => x * Math.PI / 180;
  const p1 = rad(lat1), p2 = rad(lat2), dp = rad(lat2-lat1), dl = rad(lon2-lon1);
  const a = Math.sin(dp/2)**2 + Math.cos(p1)*Math.cos(p2)*Math.sin(dl/2)**2;
  return 2 * R * Math.asin(Math.sqrt(a));
}

function esc(s) {
  return String(s).replaceAll("&","&amp;").replaceAll("<","&lt;").replaceAll(">","&gt;");
}

function money2(v) {
  return "$" + Number(v).toLocaleString("en-US", {minimumFractionDigits:2, maximumFractionDigits:2});
}

function stats(rows, type, field) {
  const vals = rows
    .filter(r => r.pricing_type === type)
    .map(r => r[field])
    .filter(v => v != null && Number.isFinite(Number(v)))
    .map(Number);
  const sum = vals.reduce((a,b) => a+b, 0);
  return {n: vals.length, sum, avg: vals.length ? sum / vals.length : null};
}

function calcCell(rows, type, field) {
  const s = stats(rows, type, field);
  if (!s.n) return "—";
  return money2(s.sum) + " ÷ " + s.n + " = <strong>" + money2(s.avg) + "</strong>";
}

const index = fs.readFileSync("index.html", "utf8");
const rentals = JSON.parse(extractBalanced(index, "const rentals =", "[", "]"));
const campuses = vm.runInNewContext("(" + extractBalanced(index, "const campuses =", "{", "}") + ")");
const defs = [
  {inner:0, outer:1, label:"0–1 mi"},
  {inner:1, outer:3, label:">1–3 mi"},
  {inner:3, outer:5, label:">3–5 mi"}
];

let rowsHtml = "";
for (const key of ["main","centennial","vet"]) {
  const c = campuses[key];
  for (const d of defs) {
    const rows = rentals
      .map(r => ({...r, _d:hav(c.lat,c.lon,r.lat,r.lon)}))
      .filter(r => (d.inner === 0 ? r._d >= 0 : r._d > d.inner) && r._d <= d.outer);
    rowsHtml += "\n<tr>" +
      "<td>" + esc(c.label) + "</td>" +
      "<td>" + d.label + "</td>" +
      "<td>" + rows.length + "</td>" +
      "<td>" + calcCell(rows,"Per bedroom","rent_low") + "</td>" +
      "<td>" + calcCell(rows,"Per bedroom","rent_high") + "</td>" +
      "<td>" + calcCell(rows,"Whole unit","rent_low") + "</td>" +
      "<td>" + calcCell(rows,"Whole unit","rent_high") + "</td>" +
      "</tr>";
  }
}

const section = `        <div class="use-note distance-band-method">
          <strong>Non-overlapping distance-band method:</strong> The article's distance comparison uses <strong>0–1 mile</strong>, <strong>more than 1–3 miles</strong>, and <strong>more than 3–5 miles</strong> from the selected campus reference point. A listing can appear in only one band within a campus comparison. Distances are straight-line Haversine calculations from the campus reference point. Each mean is calculated directly from the listings in that confined band: sum the numeric low rents and divide by the number of numeric low rents, then repeat for the high rents. The band means are not produced by subtracting or averaging the cumulative-radius means.
        </div>
        <div class="band-math-wrap">
          <table class="band-math-table" aria-label="Worked rent calculations for non-overlapping campus distance bands">
            <thead><tr><th>Campus</th><th>Distance band</th><th>Properties</th><th>Per bedroom low: sum ÷ n = mean</th><th>Per bedroom high: sum ÷ n = mean</th><th>Whole unit low: sum ÷ n = mean</th><th>Whole unit high: sum ÷ n = mean</th></tr></thead>
            <tbody>${rowsHtml}\n</tbody>
          </table>
        </div>
        <div class="filter-note">
          <strong>Cumulative-radius audit:</strong> The audit page preserves the original <strong>≤ 1, ≤ 3 and ≤ 5 mile</strong> views for source checking. Those rows intentionally overlap: ≤ 3 miles repeats the ≤ 1-mile listings, and ≤ 5 miles repeats listings from both smaller radii. Each XLSX labels the cumulative sheets as overlapping and includes a <strong>Distance Band</strong> tab containing every listing in the matching non-overlapping territory, its calculated distance from the campus reference point, and spreadsheet SUM, COUNT and AVERAGE checks.
        </div>

`;

let refs = fs.readFileSync("references.html", "utf8");
const startMarker = '        <div class="use-note distance-band-method">';
const endMarker = '        <div class="use-note">\n          <strong>Article use:</strong>';
const start = refs.indexOf(startMarker);
const end = refs.indexOf(endMarker, start);
if (start < 0 || end < 0) throw new Error("Distance-band reference section boundaries not found");
refs = refs.slice(0, start) + section + refs.slice(end);
fs.writeFileSync("references.html", refs);

console.log("Band rows written:");
for (const key of ["main","centennial","vet"]) {
  const c = campuses[key];
  for (const d of defs) {
    const rows = rentals.map(r => ({...r,_d:hav(c.lat,c.lon,r.lat,r.lon)})).filter(r => (d.inner===0?r._d>=0:r._d>d.inner) && r._d<=d.outer);
    const pl = stats(rows,"Per bedroom","rent_low"), ph = stats(rows,"Per bedroom","rent_high");
    const wl = stats(rows,"Whole unit","rent_low"), wh = stats(rows,"Whole unit","rent_high");
    console.log(c.label, d.label, "n=" + rows.length,
      "per=" + (pl.n?money2(pl.avg):"—") + "–" + (ph.n?money2(ph.avg):"—"),
      "whole=" + (wl.n?money2(wl.avg):"—") + "–" + (wh.n?money2(wh.avg):"—"));
  }
}
