/*
NC State Off-Campus Housing Data Collector
==========================================

Run from:
https://offcampus.dasa.ncsu.edu/housing

How:
Open Developer Tools > Console, paste this entire file, press Enter.

Outputs:
- ncsu-rentals-full-raw-and-derived.json
- ncsu-properties.csv
- ncsu-floorplans.csv
- ncsu-properties.geojson

Notes:
- Uses the site's own JSON endpoints.
- Runs in the current browser session.
- Does not require copied Cookie headers.
- Uses the unrestricted /housing search, not a map-bounds search.
*/

(async () => {
  const SEED = 8539;
  const SEARCH_VERSION = 4;
  const DETAIL_VERSION = 5;
  const LOCALE = "en";

  // Delay between detail requests. Increase this if the site starts returning errors.
  const DETAIL_DELAY_MS = 300;
  const PAGE_DELAY_MS = 400;
  const DOWNLOAD_DELAY_MS = 700;

  const sleep = ms => new Promise(resolve => setTimeout(resolve, ms));

  async function fetchJSON(url) {
    const response = await fetch(url, {
      headers: {
        "Accept": "application/json, text/plain, */*"
      }
    });

    if (!response.ok) {
      throw new Error(`${response.status} ${response.statusText}: ${url}`);
    }

    return response.json();
  }

  function searchEndpoint(path) {
    return (
      "/bff/listing/search/combined?url=" +
      encodeURIComponent(path) +
      `&v=${SEARCH_VERSION}&seed=${SEED}&locale=${LOCALE}`
    );
  }

  function detailEndpoint(siteId) {
    return (
      `/bff/listing/${encodeURIComponent(siteId)}` +
      `?campus=&v=${DETAIL_VERSION}&locale=${LOCALE}`
    );
  }

  function download(filename, data, mime = "application/json") {
    const contents =
      typeof data === "string"
        ? data
        : JSON.stringify(data, null, 2);

    const blob = new Blob([contents], { type: mime });
    const url = URL.createObjectURL(blob);

    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    a.remove();

    setTimeout(() => URL.revokeObjectURL(url), 2000);
  }

  function csvEscape(value) {
    if (value === null || value === undefined) return "";

    if (typeof value === "object") {
      value = JSON.stringify(value);
    }

    return `"${String(value).replaceAll('"', '""')}"`;
  }

  function makeCSV(rows) {
    if (!rows.length) return "";

    const columns = [
      ...new Set(rows.flatMap(row => Object.keys(row)))
    ];

    return [
      columns.join(","),
      ...rows.map(row =>
        columns.map(column => csvEscape(row[column])).join(",")
      )
    ].join("\n");
  }

  console.log("Fetching unrestricted search page 1...");

  const first = await fetchJSON(
    searchEndpoint("/housing")
  );

  const metadata = first.data?.metadata ?? {};
  const totalPages = metadata.totalPages ?? 1;

  console.log("Search metadata:", metadata);

  console.log(
    `Reported: ${metadata.totalResults ?? "?"} totalResults, ` +
    `${metadata.totalExact ?? "?"} exact listings, ` +
    `${metadata.totalPins ?? "?"} pins, ` +
    `${totalPages} pages`
  );

  // ----------------------------
  // SEARCH PAGES
  // ----------------------------

  const searchPages = [first];

  for (let page = 2; page <= totalPages; page++) {
    console.log(`Fetching search page ${page}/${totalPages}...`);

    const result = await fetchJSON(
      searchEndpoint(`/housing/page-${page}`)
    );

    searchPages.push(result);
    await sleep(PAGE_DELAY_MS);
  }

  // ----------------------------
  // UNIQUE EXACT PROPERTY RECORDS
  // ----------------------------

  const allPlacards = searchPages.flatMap(
    page => page.data?.placards ?? []
  );

  const properties = Array.from(
    new Map(
      allPlacards
        .filter(item => item?.siteId)
        .map(item => [item.siteId, item])
    ).values()
  );

  console.log(
    `Collected ${properties.length} unique exact property listings.`
  );

  if (
    metadata.totalExact !== undefined &&
    metadata.totalExact !== null &&
    properties.length !== metadata.totalExact
  ) {
    console.warn(
      `WARNING: API reports ${metadata.totalExact} exact results, ` +
      `but ${properties.length} unique property records were collected.`
    );
  }

  // ----------------------------
  // UNIQUE MAP PINS
  // ----------------------------

  const allPins = searchPages.flatMap(
    page => page.data?.pins ?? []
  );

  const pins = Array.from(
    new Map(
      allPins
        .filter(item => item?.siteId)
        .map(item => [item.siteId, item])
    ).values()
  );

  console.log(`Collected ${pins.length} unique pins.`);

  // ----------------------------
  // COMPLETE PROPERTY DETAIL REQUESTS
  // ----------------------------

  const details = {};
  const detailErrors = [];

  for (let i = 0; i < properties.length; i++) {
    const property = properties[i];
    const siteId = property.siteId;

    console.log(
      `Detail ${i + 1}/${properties.length}: ` +
      `${property.name || siteId}`
    );

    try {
      const result = await fetchJSON(
        detailEndpoint(siteId)
      );

      // Store the complete raw API response.
      details[siteId] = result;
    } catch (error) {
      console.error(`Failed ${siteId}`, error);

      detailErrors.push({
        siteId,
        name: property.name ?? "",
        error: String(error)
      });
    }

    await sleep(DETAIL_DELAY_MS);
  }

  // ----------------------------
  // PROPERTY TABLE
  // ----------------------------

  const propertyRows = properties.map(property => {
    const geography = property.geography ?? {};
    const summary = property.floorPlanSummary ?? {};
    const matching = summary.matching ?? {};
    const beds = matching.beds ?? {};
    const price = matching.price ?? {};
    const college = geography.targetCollege ?? {};
    const detail = details[property.siteId]?.data ?? {};

    const rentLow =
      Number.isFinite(price.low) && price.low > 0
        ? price.low
        : null;

    const rentHigh =
      Number.isFinite(price.high) && price.high > 0
        ? price.high
        : null;

    return {
      site_id: property.siteId ?? "",
      ocp_id: property.ocpId ?? "",
      apartments_listing_key: property.aptsListingKey ?? "",

      name: property.name ?? "",

      street_address: geography.streetAddress ?? "",
      city: geography.cityName ?? "",
      state: geography.stateCode ?? "",
      zip: geography.zipCode ?? "",

      latitude: geography.latitude ?? null,
      longitude: geography.longitude ?? null,

      target_campus: college.name ?? "",
      api_distance_to_campus_miles: college.distance ?? null,

      rent_low: rentLow,
      rent_high: rentHigh,
      rent_display: price.formatted ?? "",

      beds_low: beds.low ?? null,
      beds_high: beds.high ?? null,
      beds_display: beds.formatted ?? "",

      per_bed_pricing: summary.hasPerBedPricing ?? null,
      per_semester_pricing: summary.hasPerSemesterPricing ?? null,

      total_monthly_price: property.totalMonthlyPrice ?? "",
      total_monthly_price_verified: property.isTotalMonthlyPrice ?? null,

      shared_space: property.isSharedSpace ?? false,
      sublet: property.isSublet ?? false,

      lease_term: property.standardLeaseTerm ?? "",

      hide_address: property.hideAddress ?? null,
      hide_map_pin: property.hideMapPin ?? null,

      last_updated: property.lastUpdated ?? "",

      property_type:
        detail.propertyType ??
        detail.propertyStyle ??
        "",

      total_units: detail.totalUnits ?? null,
      active: detail.isActive ?? null,

      image_count:
        property.imageCount ??
        detail.imageCount ??
        null,

      listing_url:
        property.profileUrl
          ? `https://offcampus.dasa.ncsu.edu${property.profileUrl}`
          : ""
    };
  });

  // ----------------------------
  // FLOOR PLAN TABLE
  // ----------------------------

  const floorPlanRows = [];

  for (const property of properties) {
    const detail = details[property.siteId]?.data;
    if (!detail) continue;

    for (const floorPlan of detail.floorPlans ?? []) {
      floorPlanRows.push({
        site_id: property.siteId,
        property_name: property.name ?? "",

        floorplan_id: floorPlan.id ?? "",
        unit_key: floorPlan.unitKey ?? "",
        name: floorPlan.name ?? "",

        beds: floorPlan.beds ?? null,
        baths: floorPlan.baths ?? null,

        price_low:
          Number.isFinite(floorPlan.priceLow) && floorPlan.priceLow > 0
            ? floorPlan.priceLow
            : null,

        price_high:
          Number.isFinite(floorPlan.priceHigh) && floorPlan.priceHigh > 0
            ? floorPlan.priceHigh
            : null,

        price_range: floorPlan.priceRange ?? "",
        all_in_price_range: floorPlan.allInPriceRange ?? "",

        per_bed_pricing: floorPlan.perBedPricing ?? null,

        square_feet: floorPlan.squareFeet ?? "",

        units_available: floorPlan.unitsAvailable ?? null,
        availability: floorPlan.availability ?? "",
        availability_description:
          floorPlan.availabilityDescription ?? "",

        available_date: floorPlan.availableDate ?? "",

        deposit: floorPlan.deposit ?? null,
        deposit_description:
          floorPlan.depositDescription ?? "",

        application_fees:
          floorPlan.applicationFees ?? null,

        admin_fee:
          floorPlan.adminFee ?? null,

        max_occupants:
          floorPlan.maxOccupants ?? null,

        unit_number:
          floorPlan.unitNumber ?? "",

        is_unit:
          floorPlan.isUnit ?? null,

        is_new:
          floorPlan.isNew ?? null,

        raw_unit_floorplans:
          floorPlan.unitFloorplans ?? []
      });
    }
  }

  // ----------------------------
  // GEOJSON
  // ----------------------------

  const geojson = {
    type: "FeatureCollection",

    features: propertyRows
      .filter(
        property =>
          Number.isFinite(property.latitude) &&
          Number.isFinite(property.longitude)
      )
      .map(property => ({
        type: "Feature",

        geometry: {
          type: "Point",
          coordinates: [
            property.longitude,
            property.latitude
          ]
        },

        properties: Object.fromEntries(
          Object.entries(property).filter(
            ([key]) =>
              key !== "latitude" &&
              key !== "longitude"
          )
        )
      }))
  };

  // ----------------------------
  // MASTER LOSSLESS ARCHIVE
  // ----------------------------

  const master = {
    scrape: {
      scraped_at: new Date().toISOString(),

      source:
        "https://offcampus.dasa.ncsu.edu/housing",

      search_endpoint:
        "/bff/listing/search/combined",

      detail_endpoint_pattern:
        "/bff/listing/{siteId}",

      search_version: SEARCH_VERSION,
      detail_version: DETAIL_VERSION,
      locale: LOCALE,
      seed: SEED
    },

    counts: {
      api_total_results:
        metadata.totalResults ?? null,

      api_total_exact:
        metadata.totalExact ?? null,

      api_total_pages:
        metadata.totalPages ?? null,

      api_total_pins:
        metadata.totalPins ?? null,

      collected_unique_properties:
        properties.length,

      collected_unique_pins:
        pins.length,

      successful_detail_requests:
        Object.keys(details).length,

      failed_detail_requests:
        detailErrors.length,

      floorplan_rows:
        floorPlanRows.length
    },

    metadata,

    // Untouched API responses
    search_pages_raw: searchPages,
    properties_raw: properties,
    pins_raw: pins,
    details_raw: details,

    detail_errors: detailErrors,

    // Analysis-ready derived records
    derived: {
      properties: propertyRows,
      floorplans: floorPlanRows,
      geojson
    }
  };

  console.log("====== FINISHED ======");
  console.log(master.counts);
  console.table(propertyRows.slice(0, 10));

  // Download the master archive first.
  download(
    "ncsu-rentals-full-raw-and-derived.json",
    master
  );

  await sleep(DOWNLOAD_DELAY_MS);

  download(
    "ncsu-properties.csv",
    makeCSV(propertyRows),
    "text/csv;charset=utf-8"
  );

  await sleep(DOWNLOAD_DELAY_MS);

  download(
    "ncsu-floorplans.csv",
    makeCSV(floorPlanRows),
    "text/csv;charset=utf-8"
  );

  await sleep(DOWNLOAD_DELAY_MS);

  download(
    "ncsu-properties.geojson",
    geojson,
    "application/geo+json"
  );

  return master;
})();
