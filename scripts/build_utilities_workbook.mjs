/** Build the utility audit workbook with @oai/artifact-tool. */
import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { Workbook, SpreadsheetFile } from '@oai/artifact-tool';

const root = path.resolve(process.argv[2] || path.dirname(path.dirname(fileURLToPath(import.meta.url))));
const csvPath = path.join(root, 'data/audits/ncsu-room-utilities-audit.csv');
const outPath = path.join(root, 'data/audits/ncsu-room-utilities-audit.xlsx');

function parseCsv(text) {
  const rows = [];
  let row = [], field = '', quoted = false;
  for (let i = 0; i < text.length; i++) {
    const c = text[i];
    if (quoted) {
      if (c === '"' && text[i + 1] === '"') { field += '"'; i++; }
      else if (c === '"') quoted = false;
      else field += c;
    } else {
      if (c === '"') quoted = true;
      else if (c === ',') { row.push(field); field = ''; }
      else if (c === '\n') { row.push(field.replace(/\r$/, '')); rows.push(row); row = []; field = ''; }
      else field += c;
    }
  }
  if (field.length || row.length) { row.push(field); rows.push(row); }
  return rows;
}
function col(i) {
  let s = '';
  for (i++; i; i = Math.floor((i - 1) / 26)) s = String.fromCharCode(65 + (i - 1) % 26) + s;
  return s;
}
function q(s) { return String(s ?? '').replaceAll('"', '""'); }

const parsed = parseCsv((await fs.readFile(csvPath, 'utf8')).replace(/^\uFEFF/, ''));
const headers = parsed[0];
const ix = Object.fromEntries(headers.map((h, i) => [h, i]));
const rows = parsed.slice(1).filter(r => r.length === headers.length).map(r => Object.fromEntries(headers.map((h, i) => [h, r[i]])));
if (rows.length !== 41) throw new Error('Expected 41 utility-including rows, got ' + rows.length);
const all8 = rows.filter(r => r.all_utilities_explicit_manual === 'Yes');
if (all8.length !== 8) throw new Error('Expected 8 all-utilities rows, got ' + all8.length);

const wb = Workbook.create();
const red = '#8B1F2D', soft = '#F8F6F1', head = '#E9E4DB', sum = '#F3F0E9';
const money = '$#,##0.00;($#,##0.00);"$0.00"';

function buildSheet(name, data, title, subtitle) {
  const sh = wb.worksheets.add(name);
  sh.mergeCells('A1:M1');
  sh.getRange('A1').values = [[title]];
  sh.getRange('A1:M1').format.fill = red;
  sh.getRange('A1:M1').format.font = { name: 'Arial', size: 15, bold: true, color: '#FFFFFF' };
  sh.mergeCells('A2:M3');
  sh.getRange('A2').values = [[subtitle]];
  sh.getRange('A2:M3').format.fill = soft;
  sh.getRange('A2:M3').format.font = { name: 'Arial', size: 10, color: '#4F4A43' };
  sh.getRange('A2:M3').format.wrapText = true;

  const hs = ['Listing ID','Listing','Advertised price','Rent low','Rent high','Midpoint','Distance (mi)','Basis','All utilities explicit?','Evidence','Original listing URL','Internet/Wi-Fi explicit?','Internet/Wi-Fi evidence'];
  sh.getRange('A5:M5').values = [hs];
  sh.getRange('A5:M5').format.fill = head;
  sh.getRange('A5:M5').format.font = { name: 'Arial', size: 10, bold: true };
  sh.getRange('A5:M5').format.wrapText = true;

  const vals = data.map(r => [
    r.listing_id,
    r.listing,
    r.advertised_price,
    Number(r.rent_low_numeric),
    Number(r.rent_high_numeric),
    null,
    Number(r.distance_miles),
    r.any_utility_classification_basis,
    r.all_utilities_explicit_manual,
    r.all_utilities_exact_wording || r.description_utility_wording_verbatim || r.portal_utility_line_items_verbatim,
    r.original_listing_url,
    r.internet_wifi_explicit,
    r.internet_wifi_evidence
  ]);
  const first = 6, last = first + vals.length - 1;
  sh.getRange(`A${first}:M${last}`).values = vals;
  sh.getRange(`F${first}`).formulas = [[`=AVERAGE(D${first}:E${first})`]];
  sh.getRange(`F${first}:F${last}`).fillDown();
  sh.getRange(`D${first}:F${last}`).format.numberFormat = money;
  sh.getRange(`G${first}:G${last}`).format.numberFormat = '0.000';
  sh.getRange(`A${first}:M${last}`).format.wrapText = true;

  const count = last + 2, total = last + 3, mean = last + 4, check = last + 5, median = last + 6;
  sh.getRange(`A${count}:C${median}`).values = [
    ['COUNT','Listing count',''],
    ['SUM','Sum of rent values',''],
    ['MEAN','Mean advertised rent',''],
    ['SUM ÷ COUNT CHECK','Explicit check',''],
    ['MEDIAN','Median advertised rent','']
  ];
  sh.getRange(`D${count}:F${count}`).formulas = [[`=COUNT(D${first}:D${last})`,`=COUNT(E${first}:E${last})`,`=COUNT(F${first}:F${last})`]];
  sh.getRange(`D${total}:F${total}`).formulas = [[`=SUM(D${first}:D${last})`,`=SUM(E${first}:E${last})`,`=SUM(F${first}:F${last})`]];
  sh.getRange(`D${mean}:F${mean}`).formulas = [[`=AVERAGE(D${first}:D${last})`,`=AVERAGE(E${first}:E${last})`,`=AVERAGE(F${first}:F${last})`]];
  sh.getRange(`D${check}:F${check}`).formulas = [[`=D${total}/D${count}`,`=E${total}/E${count}`,`=F${total}/F${count}`]];
  sh.getRange(`D${median}:F${median}`).formulas = [[`=MEDIAN(D${first}:D${last})`,`=MEDIAN(E${first}:E${last})`,`=MEDIAN(F${first}:F${last})`]];
  sh.getRange(`A${count}:M${median}`).format.fill = sum;
  sh.getRange(`A${count}:M${median}`).format.font = { name: 'Arial', size: 10, bold: true };
  sh.getRange(`D${total}:F${median}`).format.numberFormat = money;

  const widths = [14,38,15,12,12,12,12,29,19,52,44,18,44];
  widths.forEach((w, i) => sh.getRange(`${col(i)}:${col(i)}`).format.columnWidth = w);
  sh.freezePanes.freezeRows(5);
  return { sh, first, last, count, total, mean, check, median };
}

const a = buildSheet(
  'Any utility included (41)',
  rows,
  'Utility Audit — At Least One Core Utility Included',
  '41 of 74 Main Campus private-bedroom analytic listings (55.4%) explicitly establish at least one core utility as included through saved portal utility fields, saved listing wording or both. The original 76-listing bedroom review remains preserved separately.'
);
const b = buildSheet(
  'All utilities stated (8)',
  all8,
  'Utility Audit — Explicitly States All Utilities Included',
  '8 of 74 Main Campus private-bedroom analytic listings (10.8%) explicitly state in saved wording that all utilities are included or the rent is inclusive of all utilities. The 6 listings that also explicitly include internet or Wi-Fi are highlighted in green; their median advertised midpoint is $800 per month.'
);


// Highlight the six all-utilities listings that also explicitly include internet/Wi-Fi.
const internetRows = [];
for (let j = 0; j < all8.length; j++) {
  if (all8[j].internet_wifi_explicit === 'Yes') {
    const row = b.first + j;
    internetRows.push(row);
    b.sh.getRange(`A${row}:M${row}`).format.fill = '#E2F0D9';
  }
}
if (internetRows.length !== 6) throw new Error('Expected 6 all-utilities + internet rows, got ' + internetRows.length);

// Keep the six-listing calculations on the eight-listing sheet.
const subTitle = b.median + 2;
const subCount = subTitle + 1;
const subTotal = subTitle + 2;
const subMean = subTitle + 3;
const subCheck = subTitle + 4;
const subMedian = subTitle + 5;
b.sh.mergeCells(`A${subTitle}:F${subTitle}`);
b.sh.getRange(`A${subTitle}`).values = [['GREEN ROWS — ALL UTILITIES + INTERNET/WI-FI (6)']];
b.sh.getRange(`A${subTitle}:F${subTitle}`).format.fill = '#E2F0D9';
b.sh.getRange(`A${subTitle}:F${subTitle}`).format.font = { name: 'Arial', size: 10, bold: true };
b.sh.getRange(`A${subCount}:C${subMedian}`).values = [
  ['COUNT','Highlighted listing count',''],
  ['SUM','Sum of advertised midpoints',''],
  ['MEAN','Mean advertised midpoint',''],
  ['SUM ÷ COUNT CHECK','Explicit check',''],
  ['MEDIAN','Median advertised midpoint','']
];
const midpointRefs = internetRows.map(r => `F${r}`).join(',');
b.sh.getRange(`F${subCount}`).formulas = [[`=COUNT(${midpointRefs})`]];
b.sh.getRange(`F${subTotal}`).formulas = [[`=SUM(${midpointRefs})`]];
b.sh.getRange(`F${subMean}`).formulas = [[`=AVERAGE(${midpointRefs})`]];
b.sh.getRange(`F${subCheck}`).formulas = [[`=F${subTotal}/F${subCount}`]];
b.sh.getRange(`F${subMedian}`).formulas = [[`=MEDIAN(${midpointRefs})`]];
b.sh.getRange(`A${subCount}:M${subMedian}`).format.fill = sum;
b.sh.getRange(`A${subCount}:M${subMedian}`).format.font = { name: 'Arial', size: 10, bold: true };
b.sh.getRange(`F${subTotal}:F${subMedian}`).format.numberFormat = money;

wb.recalculate();
const aMean = a.sh.getRange(`F${a.mean}`).values[0][0];
const bMean = b.sh.getRange(`F${b.mean}`).values[0][0];
if (Math.abs(aMean - 878.109756097561) > 1e-7) throw new Error('41-listing mean mismatch: ' + aMean);
if (Math.abs(bMean - 823.25) > 1e-7) throw new Error('8-listing mean mismatch: ' + bMean);
const bMedian = b.sh.getRange(`F${b.median}`).values[0][0];
const sixCount = b.sh.getRange(`F${subCount}`).values[0][0];
const sixMean = b.sh.getRange(`F${subMean}`).values[0][0];
const sixMedian = b.sh.getRange(`F${subMedian}`).values[0][0];
if (Math.abs(bMedian - 840.5) > 1e-7) throw new Error('8-listing median mismatch: ' + bMedian);
if (sixCount !== 6) throw new Error('6-listing count mismatch: ' + sixCount);
if (Math.abs(sixMean - 815.8333333333334) > 1e-7) throw new Error('6-listing mean mismatch: ' + sixMean);
if (Math.abs(sixMedian - 800) > 1e-7) throw new Error('6-listing median mismatch: ' + sixMedian);
console.log((await wb.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!|#SPILL!|#CALC!',options:{useRegex:true,maxResults:20},maxChars:1200})).ndjson);

const xlsx = await SpreadsheetFile.exportXlsx(wb);
await xlsx.save(outPath);
console.log('Exported utility audit: 41 utility-including rows; 8 all-utilities rows; 6 green internet/Wi-Fi rows.');
