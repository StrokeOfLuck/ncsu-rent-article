# NCSU Rent Article

Working data-journalism project examining advertised rental prices around NC State University campuses.

This is a source checkpoint for the article and interactive map as of September 9, 2026. The project is still in development and is not yet linked from the public portfolio site.

## Quick links

- [Open the main interactive](https://strokeofluck.github.io/ncsu-rent-article/)
- [Open the reporting references](https://strokeofluck.github.io/ncsu-rent-article/references.html)

## Current analysis (revised September 13, 2026)

The website and references use `data/reviewed-rentals.json` and `assets/rent-analysis.js`.
The September 9 source CSVs remain unchanged. The review layer records original and
revised pricing categories, exclusion reasons, move-in flags, source URLs and hashes.

- One observation is a portal listing ID, not necessarily a distinct building or vacant unit.
- 168 saved IDs; 156 within five miles of at least one of three campus reference points.
- 23 room/suite category corrections. Mixed or unresolved bases and search/detail price
  mismatches are excluded. In the combined geography: 78 usable room/per-bedroom
  prices and 53 whole-unit prices; 25 prices excluded but still visible for review.
- Three disjoint distance bands per campus: 0–1, >1–3 and >3–5 miles. Campus cards pool
  all eligible listings within five miles. The combined comparison deduplicates IDs.
- Both positive numeric endpoints are required. Means use the same paired denominator;
  missing and zero-placeholder prices never enter a mean. The personal chart uses
  room mean/median midpoints. Optional aid checkboxes model the full CDS averages
  with tuition/fees covered separately; custom net-aid inputs are tucked into an
  optional panel. Whole-unit rent is not assigned to a presumed student.
- This is an advertised-offer convenience sample, including future dates and varied
  lease terms. It does not establish market coverage, current vacancies, students'
  actual housing burden or a causal effect of distance on rent.

The complete [Excel formula audit](data/audits/ncsu-rent-audit.xlsx) replaces the old
browser-generated cumulative-radius workbooks. It contains raw source tables, linked
floor-plan checks, review inputs, Haversine/band formulas, all campus/band summaries,
sensitivity analyses, all aid-checkbox combinations, custom budget calculations and
official housing-rate changes. Counts use plain labels, with exclusions shown so
category counts reconcile to total listings.
The [map checker](https://strokeofluck.github.io/ncsu-rent-article/rental-map-audit.html)
filters all three campuses by band, price inclusion, category and text.

## Rebuild and verify

```sh
python scripts/build_analysis.py
python scripts/build_references.py
python scripts/prepare_workbook_sources.py
node scripts/build_workbook.mjs
python scripts/verify_audit.py
```

Workbook generation requires `@oai/artifact-tool` in the Node environment. It uses
ordinary Excel formulas, verifies recalculated values against the website's arithmetic,
and exports the downloadable workbook. The temporary `source-tables.json` and render
checks are not published. No npm build is needed to serve the static site.

`scripts/build_analysis.py` derives automatic checks from the saved CSVs.
`data/review-decisions.json` holds additional evidence decisions. Resolve a flagged
record against source evidence before changing its status; never silently replace an
old snapshot price with a new live price. Rebuild the data bundle and workbook together.
`docs/revised-methods.html` is the reference-method template; the remaining historical
source cards are retained in `references.html`. `assets/reference-math.js` calculates
worked examples from the same reviewed dataset as the article.

## Rental source

[NC State Off-Campus Housing](https://offcampus.dasa.ncsu.edu/housing), collected
September 9, 2026. Original collection log timestamp: `2026-09-09T02:24:45.953Z`.
The log reported 527 total results, 168 exact records/map pins and five pages.
The committed CSVs verify 168 unique records and 537 nested floor-plan rows, not
complete coverage of all 527 results. Original lossless backend responses are not
committed; preserve them privately for future collection audits.

## Campus GIS

Campus boundaries and building footprints came from NC State Facilities GIS downloads supplied September 2026.

For the story interface:

- Main Campus highlights Central Campus, North Campus and South Campus precincts
- Centennial highlights the Centennial Campus precinct
- Centennial Biomedical Campus (College of Veterinary Medicine) view uses the West Campus precinct geometry from the Facilities GIS layer

The statewide `Outlying` perimeter was omitted from the Raleigh-focused map.

## Data files

`data/ncsu-properties.csv` contains one row per unique exact property/listing.

`data/ncsu-floorplans.csv` contains the detailed floor-plan records returned by the property-detail API.

`data/ncsu-amenities.csv`, `data/ncsu-fees.csv` and `data/ncsu-college-distances.csv` preserve additional derived tables from the scrape.

`data/ncsu-properties.geojson` contains mapped property points.

`data/ncsu-campus-perimeters.geojson` and `data/ncsu-campus-buildings.geojson` are web-ready conversions of the official NC State GIS layers used in the map.

## Privacy / publication note

The NC State portal marks some listings with `hide_address = true`. Exact street-address text for those records has been removed from the public Git checkpoint and from the embedded map data. The original lossless raw scrape is intentionally not committed to this public portfolio repository because it preserves the portal's raw responses, including fields that should not be republished blindly.

## Scraper

`scripts/ncsu-rental-scraper.js` is the browser-console collector used for this scrape. See `docs/scraper-README.md` for collection and rerun instructions.

The script does not store copied browser cookies or login credentials.

## Reporting language

Preferred source description:

> Listings advertised through NC State's Off-Campus Housing website, collected on September 9, 2026.

This dataset should not be described as every rental available around NC State or Raleigh.
