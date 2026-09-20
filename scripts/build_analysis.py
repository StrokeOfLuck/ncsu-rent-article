"""Build a reviewable analysis layer; never overwrite the September 9 source CSVs."""
import csv
import hashlib
import json
import math
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data'
REVIEWED = '2026-09-20'
CAMPUS = {
    'main': {'label': 'Main Campus', 'lat': 35.77951, 'lon': -78.68168},
    'centennial': {'label': 'Centennial Campus', 'lat': 35.7687, 'lon': -78.6775},
    'vet': {'label': 'Centennial Biomedical Campus', 'lat': 35.79847, 'lon': -78.70408},
}

def number(x):
    try:
        n = float(x)
        return n if math.isfinite(n) and n > 0 else None
    except (ValueError, TypeError):
        return None

def hav(a, b, c, d):
    a, b, c, d = map(math.radians, [a, b, c, d])
    h = math.sin((c-a)/2)**2 + math.cos(a)*math.cos(c)*math.sin((d-b)/2)**2
    return 2*3958.7613*math.atan2(math.sqrt(h), math.sqrt(max(0, 1-h)))

def band(d):
    return '0–1 mi' if d <= 1 else '>1–3 mi' if d <= 3 else '>3–5 mi' if d <= 5 else 'Outside 5 mi'

def read(name):
    return list(csv.DictReader((DATA / name).open()))

properties = read('ncsu-properties.csv')
floorplans = read('ncsu-floorplans.csv')
fp_by_id = {p['site_id']: [f for f in floorplans if f['site_id'] == p['site_id']] for p in properties}
overrides = json.loads((DATA / 'review-decisions.json').read_text())
rows = []
for p in properties:
    fs = fp_by_id[p['site_id']]
    low, high = number(p['rent_low']), number(p['rent_high'])
    original = 'Per bedroom' if p['per_bed_pricing'].lower() == 'true' else 'Whole unit'
    category = original
    reasons, flags = [], []
    note = 'Source pricing flag retained; automated consistency checks passed. This is not independent landlord verification.'
    if p['name'].lower().startswith('room in ') and original == 'Whole unit':
        category = 'Per bedroom'
        flags.append('room_title_override')
        note = 'Saved September 9 title explicitly offers a room. Reclassified from whole unit to room/per-bedroom; snapshot price unchanged.'
    decision = overrides.get(p['site_id'], {})
    if 'category' in decision:
        category = decision['category']
        flags.append('description_override')
    if decision.get('note'):
        note = decision['note']
    fp_types = {f['per_bed_pricing'].lower() for f in fs}
    mixed = len(fp_types) > 1 or decision.get('exclude_basis', False)
    if mixed:
        reasons.append('Unresolved pricing basis')
        flags.append('pricing_basis_review')
        category = 'Review'
        if not decision.get('note'):
            note = 'Saved floor plans contain both per-bedroom and whole-unit flags. A single property range cannot be assigned a reliable common pricing basis; no division by bedroom count or price substitution.'
    fl = [number(f['price_low']) for f in fs if number(f['price_low']) is not None]
    fh = [number(f['price_high']) for f in fs if number(f['price_high']) is not None]
    fp_low, fp_high = min(fl) if fl else None, max(fh) if fh else None
    conflict = low is not None and high is not None and fp_low is not None and fp_high is not None and (low != fp_low or high != fp_high)
    if low is None or high is None or low > high:
        reasons.append('Missing or invalid price pair')
        flags.append('missing_price')
    if conflict:
        reasons.append('Search/detail price mismatch')
        flags.append('price_mismatch')
        note += f' Search summary: ${low:g}–${high:g}; saved floor-plan envelope: ${fp_low:g}–${fp_high:g}. Difference may reflect fees, timing or scope; unresolved snapshot price excluded.'
    dates = [f['available_date'][:10] for f in fs if f['available_date']]
    future_only = bool(fs) and len(dates) == len(fs) and all(d >= '2027-01-01' for d in dates)
    if future_only:
        flags.append('all_floorplans_2027_or_later')
    if 'waitlist' in p['name'].lower() or any('waitlist' in f['availability'].lower() for f in fs):
        flags.append('waitlist_mentioned')
    if not p['lease_term']:
        flags.append('lease_term_missing')
    allin_diff = any(f['all_in_price_range'] and f['all_in_price_range'] != f['price_range'] for f in fs)
    if allin_diff:
        flags.append('floorplan_all_in_differs')
    if decision.get('exclude_occupancy'):
        reasons.append('Bedroom occupancy review: ' + decision['exclude_occupancy'])
        flags.append('bedroom_occupancy_exclusion')
    if p['site_id'] == '7e6kx1w':
        flags.append('high_endpoint_review')
        note = 'Portal explicitly labels the entire $599–$2,157 range per bedroom (reviewed September 13). Retained as reported, but the high endpoint needs landlord confirmation. Sensitivity results also omit this listing; no assumed division by three.'
    r = {
        'site_id': p['site_id'], 'name': p['name'], 'address': p['street_address'],
        'city': p['city'], 'state': p['state'], 'zip': p['zip'],
        'lat': float(p['latitude']), 'lon': float(p['longitude']),
        'rent_low': low, 'rent_high': high, 'rent_display': p['rent_display'],
        'original_pricing_type': original, 'pricing_type': category,
        'beds_low': float(p['beds_low']) if p['beds_low'] else None,
        'beds_high': float(p['beds_high']) if p['beds_high'] else None,
        'beds_display': p['beds_display'], 'property_type': p['property_type'],
        'shared_space': p['shared_space'].lower() == 'true', 'sublet': p['sublet'].lower() == 'true',
        'lease_term': p['lease_term'], 'last_updated': p['last_updated'],
        'listing_url': p['listing_url'], 'eligible_price': not reasons,
        'review_status': 'Excluded from rent means' if reasons else 'Included in rent means',
        'exclusion_reason': '; '.join(reasons), 'review_note': note,
        'review_date': REVIEWED, 'flags': flags, 'floorplan_count': len(fs),
        'floorplan_low': fp_low, 'floorplan_high': fp_high,
        'earliest_date': min(dates) if dates else '', 'latest_date': max(dates) if dates else '',
        'all_2027_or_later': future_only, 'all_in_differs': allin_diff,
    }
    for key, c in CAMPUS.items():
        d = hav(c['lat'], c['lon'], r['lat'], r['lon'])
        r[f'distance_{key}'] = d
        r[f'band_{key}'] = band(d)
        r[f'boundary_feet_{key}'] = min(abs(d-b) for b in [1, 3, 5])*5280
    r['in_union'] = any(r[f'distance_{key}'] <= 5 for key in CAMPUS)
    rows.append(r)

assert len({r['site_id'] for r in rows}) == len(rows)
bundle = {
    'version': '2026-09-20.1', 'snapshot_date': '2026-09-09', 'review_date': REVIEWED,
    'scope': 'All advertised offers in the saved snapshot, regardless of move-in date; not an available-now inventory.',
    'source_commit': '23a0fb6522cb13b0a4a243318599749cb406ec08',
    'raw_sha256': {n: hashlib.sha256((DATA / n).read_bytes()).hexdigest() for n in ['ncsu-properties.csv', 'ncsu-floorplans.csv']},
    'campuses': CAMPUS, 'earth_radius_miles': 3958.7613, 'rentals': rows,
}
(DATA / 'reviewed-rentals.json').write_text(json.dumps(bundle, indent=2, ensure_ascii=False)+'\n')
(ROOT / 'assets' / 'reviewed-data.js').write_text('/* Generated by scripts/build_analysis.py. */\nwindow.RENT_DATA = '+json.dumps(bundle, ensure_ascii=False)+';\n')
with (DATA / 'reviewed-rentals.csv').open('w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0]))
    w.writeheader()
    w.writerows({**r, 'flags': '; '.join(r['flags'])} for r in rows)
print(json.dumps({'source_rows': len(rows), 'within_union': sum(r['in_union'] for r in rows), 'included_union': sum(r['eligible_price'] and r['in_union'] for r in rows), 'overrides': sum(r['original_pricing_type'] != r['pricing_type'] and r['pricing_type'] != 'Review' for r in rows), 'exclusions': [(r['site_id'], r['exclusion_reason']) for r in rows if not r['eligible_price']]}, indent=2))
