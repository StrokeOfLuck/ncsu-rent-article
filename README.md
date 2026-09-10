# NCSU Rent Article

Working data-journalism project examining advertised rental prices around NC State University campuses.

This is a source checkpoint for the article and interactive map as of September 9, 2026. The project is still in development and is not yet linked from the public portfolio site.

## Quick links

- [Open the main interactive](https://strokeofluck.github.io/ncsu-rent-article/)
- [Open the reporting references](https://strokeofluck.github.io/ncsu-rent-article/references.html)

## Current map

`index.html` contains the current interactive MapLibre preview. It includes:

- Main Campus, Centennial Campus and College of Veterinary Medicine reference views
- 1, 2, 3 and 5 mile straight-line radius calculations
- separate per-bedroom and whole-unit advertised rent summaries
- official NC State campus perimeter and building-footprint overlays
- hover details and links back to the original NC State off-campus listing
- an XLSX audit download for each cumulative radius with clearly labeled overlapping cumulative sheets plus a non-overlapping Distance Band tab containing row-level distances and calculation checks

The basemap currently uses OpenFreeMap's Positron MapLibre style for development. A later production version may use a self-hosted Raleigh-area PMTiles basemap.

## Rental source

Listings were collected from NC State's Off-Campus Housing website:

`https://offcampus.dasa.ncsu.edu/housing`

Scrape timestamp: `2026-09-09T02:24:45.953Z`

At collection time the unrestricted search reported:

- `totalResults`: 527
- `totalExact`: 168
- `totalPages`: 5
- `totalPins`: 168

The scraper successfully collected all 168 exact property records and all 168 property-detail responses. Detailed property records produced 537 floor-plan rows.

These counts describe different parts of the portal and should not be treated as interchangeable. The reporting unit for the main map is the unique property/location, not every floor plan.

## Pricing methodology

Per-bedroom pricing and whole-unit pricing are kept separate throughout the analysis.

For each radius the map displays:

- number of unique properties within the radius
- mean advertised low and mean advertised high for per-bedroom listings
- mean advertised low and mean advertised high for whole-unit listings

Nonpositive prices and listings without a numeric advertised price are excluded from the corresponding price average rather than treated as zero.

Distance is calculated from listing latitude/longitude using straight-line geographic distance rather than the portal's supplied campus-distance field. This is intentional because several portal distance values were obviously erroneous.

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
