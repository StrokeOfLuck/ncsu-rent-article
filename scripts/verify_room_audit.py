"""Verify the exported room workbook against the dated reviewed records."""
from pathlib import Path
import json
import math
import zipfile
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

root = Path(__file__).resolve().parents[1]
data = json.loads((root / 'data/reviewed-rentals.json').read_text())
raw = json.loads((root / 'data/audits/source-tables.json').read_text())
ns = {'m': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
sheets = {}
with zipfile.ZipFile(root / 'data/audits/ncsu-room-rent-audit.xlsx') as z:
    strings = [''.join(e.itertext()) for e in ET.fromstring(z.read('xl/sharedStrings.xml')).findall('m:si', ns)] if 'xl/sharedStrings.xml' in z.namelist() else []
    names = [s.attrib['name'] for s in ET.fromstring(z.read('xl/workbook.xml')).find('m:sheets', ns)]
    for number, name in enumerate(names, 1):
        values, formulas = {}, {}
        for cell in ET.fromstring(z.read(f'xl/worksheets/sheet{number}.xml')).findall('.//m:c', ns):
            v, f, kind = cell.find('m:v', ns), cell.find('m:f', ns), cell.get('t')
            text = v.text if v is not None else None
            assert kind != 'e', (name, cell.attrib, text)
            value = strings[int(text)] if kind == 's' else ''.join(cell.find('m:is', ns).itertext()) if kind == 'inlineStr' else None if text is None else text if kind in ['str', 'b'] else float(text)
            values[cell.get('r')] = value
            if f is not None:
                formulas[cell.get('r')] = f.text
        sheets[name] = values, formulas
    for file in z.namelist():
        if file.startswith('xl/tables/') and file.endswith('.xml'):
            table = ET.fromstring(z.read(file))
            if table.get('name').endswith('Prices') or table.get('name') == 'RoomExclusions':
                assert table.find('m:autoFilter', ns) is not None

def col(n):
    result = ''
    while n:
        n, remainder = divmod(n - 1, 26)
        result = chr(65 + remainder) + result
    return result

for sheet, key in [('Raw properties', 'properties'), ('Raw floorplans', 'floorplans')]:
    values = sheets[sheet][0]
    headers = list(raw[key][0])
    for j, source in enumerate(raw[key], 2):
        for i, header in enumerate(headers, 1):
            actual, expected = values.get(col(i) + str(j)), source[header]
            if expected == '':
                assert actual in [None, '']
            elif isinstance(actual, float):
                try:
                    numeric = float(expected)
                except ValueError:
                    date = datetime.fromisoformat(expected.replace('Z', '+00:00')).replace(tzinfo=timezone.utc)
                    numeric = (date - datetime(1899, 12, 30, tzinfo=timezone.utc)).total_seconds() / 86400
                assert math.isclose(actual, numeric, abs_tol=1e-8), (sheet, j, header)
            else:
                assert actual == expected, (sheet, j, header)

rooms = {r['site_id']: r for r in data['rentals'] if r['in_union'] and r['eligible_price'] and r['pricing_type'] == 'Per bedroom'}
band_counts = {}
for name, (values, formulas) in sheets.items():
    if name != 'Rooms' and not any(name.startswith(x + ' ') for x in ['Main', 'Centennial', 'Biomedical']):
        continue
    count_row = next(int(cell[1:]) for cell, value in values.items() if value == 'Prices used (COUNT)')
    last = count_row - 2
    ids = [values['F' + str(i)] for i in range(6, last + 1)]
    assert len(ids) == len(set(ids))
    if name == 'Rooms':
        expected = set(rooms)
    else:
        prefix, band, _ = name.split(' ')
        key = {'Main': 'main', 'Centennial': 'centennial', 'Biomedical': 'vet'}[prefix]
        low, high = map(int, band.split('-'))
        expected = {sid for sid, r in rooms.items() if r['distance_' + key] <= high and (low == 0 or r['distance_' + key] > low)}
        band_counts[name] = len(ids)
    assert set(ids) == expected, name
    for i, sid in enumerate(ids, 6):
        r = rooms[sid]
        assert values['A' + str(i)] == r['name']
        assert values['B' + str(i)] == r['rent_low']
        assert values['C' + str(i)] == r['rent_high']
        assert values['D' + str(i)] == (r['rent_low'] + r['rent_high']) / 2
    for c, field in [('B', 'rent_low'), ('C', 'rent_high')]:
        total = sum(rooms[sid][field] for sid in ids)
        assert values[c + str(count_row)] == len(ids)
        assert math.isclose(values[c + str(count_row + 1)], total, abs_tol=1e-8)
        assert formulas[c + str(count_row + 1)] == f'SUM({c}6:{c}{last})'
        assert math.isclose(values[c + str(count_row + 2)], total / len(ids), abs_tol=1e-8)
    mean = sum((rooms[sid]['rent_low'] + rooms[sid]['rent_high']) / 2 for sid in ids) / len(ids)
    assert math.isclose(values['D' + str(count_row + 2)], mean, abs_tol=1e-8)
excluded = {value for cell, value in sheets['Excluded'][0].items() if cell.startswith('D') and cell != 'D1'}
assert len(rooms) == 76 and len(excluded) == 92 and not set(rooms) & excluded
assert set(rooms) | excluded == {r['site_id'] for r in data['rentals']}
assert len(band_counts) == 9
print('PASS: raw data preserved, 76 rooms + 92 excluded IDs, nine band memberships, source-linked prices, SUM/count/mean formulas, cached results and native filters.')
