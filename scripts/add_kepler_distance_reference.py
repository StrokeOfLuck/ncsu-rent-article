from pathlib import Path

refs = Path("references.html")
text = refs.read_text(encoding="utf-8")

fragment = '''    <article class="ref" id="kepler-distance-audit">
      <div class="ref-head">
        <div>
          <div class="ref-no">Reference 01B</div>
          <div class="ref-title">Main Campus Distance-Band Kepler Audit</div>
        </div>
        <div class="tags">
          <span class="tag">Maps</span>
          <span class="tag">Distance audit</span>
          <span class="tag">Kepler.gl</span>
        </div>
      </div>

      <div class="ref-body">
        <div class="meta-grid">
          <div class="meta-label">Purpose</div>
          <div class="meta-value">Map-based verification of the Main Campus 0–1 mile, &gt;1–3 mile, and &gt;3–5 mile distance bands from the XLSX audits. Each listing map focuses on location, calculated distance from the Main Campus reference point, and distance to the nearest band boundary.</div>

          <div class="meta-label">0–1 mile</div>
          <div class="meta-value"><a href="https://kepler.gl/demo/map?mapUrl=https%3A%2F%2Fraw.githubusercontent.com%2FStrokeOfLuck%2Fncsu-rent-article%2Fmain%2Fdata%2Fkepler%2Fncsu-rent-main-campus_0-1mi-distance.kepler.gl.json" target="_blank" rel="noopener noreferrer">Kepler</a> · 54 listings. The point layer is on by default. Listing numbers are a separate toggleable layer; straight reference-to-listing distance checks are a separate layer and start turned off.</div>

          <div class="meta-label">&gt;1–3 miles</div>
          <div class="meta-value"><a href="https://kepler.gl/demo/map?mapUrl=https%3A%2F%2Fraw.githubusercontent.com%2FStrokeOfLuck%2Fncsu-rent-article%2Fmain%2Fdata%2Fkepler%2Fncsu-rent-main-campus_1-3mi-distance.kepler.gl.json" target="_blank" rel="noopener noreferrer">Kepler</a> · 73 listings. The point layer is on by default. Listing numbers are a separate toggleable layer; straight reference-to-listing distance checks are a separate layer and start turned off.</div>

          <div class="meta-label">&gt;3–5 miles</div>
          <div class="meta-value"><a href="https://kepler.gl/demo/map?mapUrl=https%3A%2F%2Fraw.githubusercontent.com%2FStrokeOfLuck%2Fncsu-rent-article%2Fmain%2Fdata%2Fkepler%2Fncsu-rent-main-campus_3-5mi-distance.kepler.gl.json" target="_blank" rel="noopener noreferrer">Kepler</a> · 26 listings. The shaded &gt;3–5 mile band, 3-mile boundary, 5-mile boundary, listing points, listing numbers, and Main Campus reference point are separate toggleable layers.</div>

          <div class="meta-label">Distance circles</div>
          <div class="meta-value"><a href="https://kepler.gl/demo/map?mapUrl=https%3A%2F%2Fraw.githubusercontent.com%2FStrokeOfLuck%2Fncsu-rent-article%2Fmain%2Fdata%2Fkepler%2Fncsu-rent-main-campus_radius-circles.kepler.gl.json" target="_blank" rel="noopener noreferrer">Kepler</a> · Separate 1-, 3-, and 5-mile boundary map with lightly filled 0–1, &gt;1–3, and &gt;3–5 mile bands. Every band and boundary is an independent toggleable layer.</div>

          <div class="meta-label">Band geometry</div>
          <div class="meta-value"><strong>0–1 mile</strong> is the area inside the 1-mile circle; <strong>&gt;1–3 miles</strong> is the ring between the 1- and 3-mile circles; <strong>&gt;3–5 miles</strong> is the ring between the 3- and 5-mile circles. The circle lines are boundaries, while the shaded areas are the actual non-overlapping bands.</div>

          <div class="meta-label">Distance definition</div>
          <div class="meta-value">Straight-line Haversine/geodesic distance from the Main Campus reference point at <strong>35.77951, -78.68168</strong>. This is not driving distance and is not measured from the edge of campus.</div>

          <div class="meta-label">Verification</div>
          <div class="meta-value">All 127 listing coordinates were independently recalculated. The largest difference from the workbook distance is <strong>0.0026 feet</strong>, which is rounding-level. The closest listing outside the 1-mile boundary is about <strong>140 feet</strong> beyond it, and the closest listing to the 3-mile outer boundary is about <strong>159 feet</strong> inside it.</div>
        </div>

        <div class="audit-source-note">The Kepler links use Kepler.gl's mapUrl parameter with the saved map files hosted in this repository, so clicking them opens the configured data and layers preloaded.</div>
      </div>
    </article>

'''

if 'id="kepler-distance-audit"' in text:
    start = text.index('    <article class="ref" id="kepler-distance-audit">')
    end = text.index('    </article>', start) + len('    </article>')
    text = text[:start] + fragment.rstrip() + text[end:]
else:
    marker = '          <div class="ref-no">Reference 02</div>'
    marker_pos = text.index(marker)
    article_pos = text.rfind('    <article class="ref">', 0, marker_pos)
    text = text[:article_pos] + fragment + text[article_pos:]

refs.write_text(text, encoding="utf-8")
