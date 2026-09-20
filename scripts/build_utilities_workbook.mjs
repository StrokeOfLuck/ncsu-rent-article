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
  sh.mergeCells('A1:K1');
  sh.getRange('A1').values = [[title]];
  sh.getRange('A1:K1').format.fill = red;
  sh.getRange('A1:K1').format.font = { name: 'Arial', size: 15, bold: true, color: '#FFFFFF' };
  sh.mergeCells('A2:K3');
  sh.getRange('A2').values = [[subtitle]];
  sh.getRange('A2:K3').format.fill = soft;
  sh.getRange('A2:K3').format.font = { name: 'Arial', size: 10, color: '#4F4A43' };
  sh.getRange('A2:K3').format.wrapText = true;

  const hs = ['Listing ID','Listing','Advertised price','Rent low','Rent high','Midpoint','Distance (mi)','Basis','All utilities explicit?','Evidence','Original listing'];
  sh.getRange('A5:K5').values = [hs];
  sh.getRange('A5:K5').format.fill = head;
  sh.getRange('A5:K5').format.font = { name: 'Arial', size: 10, bold: true };
  sh.getRange('A5:K5').format.wrapText = true;

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
    null
  ]);
  const first = 6, last = first + vals.length - 1;
  sh.getRange(`A${first}:K${last}`).values = vals;
  sh.getRange(`F${first}`).formulas = [[`=AVERAGE(D${first}:E${first})`]];
  sh.getRange(`F${first}:F${last}`).fillDown();
  for (let i = 0; i < data.length; i++) {
    const row = first + i;
    sh.getRange(`K${row}`).formulas = [[`=HYPERLINK("${q(data[i].original_listing_url)}","Open original listing")`]];
  }
  sh.getRange(`D${first}:F${last}`).format.numberFormat = money;
  sh.getRange(`G${first}:G${last}`).format.numberFormat = '0.000';
  sh.getRange(`A${first}:K${last}`).format.wrapText = true;

  const count = last + 2, total = last + 3, mean = last + 4, check = last + 5;
  sh.getRange(`A${count}:C${check}`).values = [
    ['COUNT','Listing count',''],
    ['SUM','Sum of rent values',''],
    ['MEAN','Mean advertised rent',''],
    ['SUM ÷ COUNT CHECK','Explicit check','']
  ];
  sh.getRange(`D${count}:F${count}`).formulas = [[`=COUNT(D${first}:D${last})`,`=COUNT(E${first}:E${last})`,`=COUNT(F${first}:F${last})`]];
  sh.getRange(`D${total}:F${total}`).formulas = [[`=SUM(D${first}:D${last})`,`=SUM(E${first}:E${last})`,`=SUM(F${first}:F${last})`]];
  sh.getRange(`D${mean}:F${mean}`).formulas = [[`=AVERAGE(D${first}:D${last})`,`=AVERAGE(E${first}:E${last})`,`=AVERAGE(F${first}:F${last})`]];
  sh.getRange(`D${check}:F${check}`).formulas = [[`=D${total}/D${count}`,`=E${total}/E${count}`,`=F${total}/F${count}`]];
  sh.getRange(`A${count}:K${check}`).format.fill = sum;
  sh.getRange(`A${count}:K${check}`).format.font = { name: 'Arial', size: 10, bold: true };
  sh.getRange(`D${total}:F${check}`).format.numberFormat = money;

  const widths = [14,38,15,12,12,12,12,29,19,52,23];
  widths.forEach((w, i) => sh.getRange(`${col(i)}:${col(i)}`).format.columnWidth = w);
  sh.freezePanes.freezeRows(5);
  return { sh, first, last, count, total, mean, check };
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
  '8 of 74 Main Campus private-bedroom analytic listings (10.8%) explicitly state in saved wording that all utilities are included or the rent is inclusive of all utilities. Six of those eight also explicitly include internet or Wi-Fi.'
);

wb.recalculate();
const aMean = a.sh.getRange(`F${a.mean}`).values[0][0];
const bMean = b.sh.getRange(`F${b.mean}`).values[0][0];
if (Math.abs(aMean - 878.109756097561) > 1e-7) throw new Error('41-listing mean mismatch: ' + aMean);
if (Math.abs(bMean - 823.25) > 1e-7) throw new Error('8-listing mean mismatch: ' + bMean);
console.log((await wb.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!|#SPILL!|#CALC!',options:{useRegex:true,maxResults:20},maxChars:1200})).ndjson);

const xlsx = await SpreadsheetFile.exportXlsx(wb);
await xlsx.save(outPath);
console.log('Exported utility audit: 41 utility-including rows; 8 all-utilities rows.');
