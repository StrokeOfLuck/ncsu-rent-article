from pathlib import Path
import re

# Update the reader-facing housing rate chart and its price-context footer.
p = Path("index.html")
s = p.read_text(encoding="utf-8")

old_css = '''.housing-rate-cpi-label{
  position:absolute;
  left:42.5%;
  top:0;
  transform:translateX(-50%);
  color:#6fb4f2;
  font-size:8.5px;
  font-weight:900;
  white-space:nowrap;
}
.housing-rate-cpi-label::after{
  content:"";
  position:absolute;
  left:50%;
  top:13px;
  height:27px;
  border-left:2px solid #6fb4f2;
  opacity:1;
}
'''
new_css = '''.housing-rate-benchmark-legend{
  display:flex;
  flex-wrap:wrap;
  align-items:center;
  gap:5px 13px;
  margin:0 0 2px;
  color:var(--muted);
  font-size:8.3px;
  line-height:1.25;
}
.housing-rate-benchmark-legend strong{
  color:#4e4a45;
  font-weight:850;
}
.housing-rate-benchmark-key{
  display:inline-flex;
  align-items:center;
  gap:5px;
  white-space:nowrap;
}
.housing-rate-benchmark-swatch{
  width:14px;
  height:0;
  flex:0 0 auto;
  border-top:2px solid #777168;
}
.housing-rate-benchmark-swatch.school{
  border-top-color:var(--blue);
  border-top-width:3px;
}
.housing-rate-benchmark-swatch.cpi{
  border-top-color:#6fb4f2;
  border-top-style:dashed;
}
.housing-rate-benchmark-line{
  position:absolute;
  top:-13px;
  bottom:-13px;
  width:0;
  z-index:1;
  pointer-events:none;
}
.housing-rate-benchmark-line.benchmark-rent{
  left:36.25%;
  border-left:1px solid #777168;
  opacity:.9;
}
.housing-rate-benchmark-line.benchmark-school{
  left:37.5%;
  border-left:2px solid var(--blue);
  opacity:.95;
}
.housing-rate-benchmark-line.benchmark-cpi{
  left:42.5%;
  border-left:2px dashed #6fb4f2;
  opacity:.85;
}
'''
if old_css in s:
    s = s.replace(old_css, new_css, 1)
elif '.housing-rate-benchmark-legend{' not in s:
    raise SystemExit("Could not find old CPI benchmark CSS")

old_plot_line = '''.housing-rate-plot::after{
  content:"";
  position:absolute;
  left:42.5%;
  top:-13px;
  bottom:-13px;
  border-left:2px solid #6fb4f2;
  opacity:.9;
  z-index:0;
  pointer-events:none;
}
'''
s = s.replace(old_plot_line, '', 1)

# The labels are now in a compact benchmark legend, so the axis itself can stay shallow.
s = s.replace('''.housing-rate-axis-plot{
  position:relative;
  height:32px;
}''', '''.housing-rate-axis-plot{
  position:relative;
  height:22px;
}''', 1)

old_axis = '''      <div class="housing-rate-chart" aria-label="Projected percentage increase in NC State housing rates from 2025–26 to 2026–27. Dots show each housing rate increase on a zero to eight percent scale. A vertical reference line marks overall U.S. CPI inflation at 3.4 percent.">
        <div class="housing-rate-axis" aria-hidden="true">
          <div></div>
          <div class="housing-rate-axis-plot">
            <span class="housing-rate-cpi-label">Overall CPI 3.4%</span>
            <span class="housing-rate-axis-tick first" style="left:0%">0%</span>
            <span class="housing-rate-axis-tick" style="left:25%">2%</span>
            <span class="housing-rate-axis-tick" style="left:50%">4%</span>
            <span class="housing-rate-axis-tick" style="left:75%">6%</span>
            <span class="housing-rate-axis-tick last" style="left:100%">8%</span>
          </div>
          <div></div>
        </div>'''
new_axis = '''      <div class="housing-rate-chart" aria-label="Projected percentage increase in NC State housing rates from 2025–26 to 2026–27. Dots show each housing rate increase on a zero to eight percent scale. Vertical reference lines show July 2026 BLS 12-month changes for rent of primary residence at 2.9 percent, lodging while at school at 3.0 percent, and all-items CPI at 3.4 percent.">
        <div class="housing-rate-benchmark-legend" aria-label="BLS price benchmarks, July 2025 to July 2026">
          <strong>BLS 12-month change:</strong>
          <span class="housing-rate-benchmark-key"><span class="housing-rate-benchmark-swatch school"></span>Lodging while at school 3.0%</span>
          <span class="housing-rate-benchmark-key"><span class="housing-rate-benchmark-swatch"></span>Rent of primary residence 2.9%</span>
          <span class="housing-rate-benchmark-key"><span class="housing-rate-benchmark-swatch cpi"></span>All items CPI 3.4%</span>
        </div>
        <div class="housing-rate-axis" aria-hidden="true">
          <div></div>
          <div class="housing-rate-axis-plot">
            <span class="housing-rate-axis-tick first" style="left:0%">0%</span>
            <span class="housing-rate-axis-tick" style="left:25%">2%</span>
            <span class="housing-rate-axis-tick" style="left:50%">4%</span>
            <span class="housing-rate-axis-tick" style="left:75%">6%</span>
            <span class="housing-rate-axis-tick last" style="left:100%">8%</span>
          </div>
          <div></div>
        </div>'''
if old_axis in s:
    s = s.replace(old_axis, new_axis, 1)
elif 'BLS 12-month change:' not in s:
    raise SystemExit("Could not find housing-rate axis markup")

marker = '<div class="housing-rate-plot"><span class="housing-rate-dot"'
line_spans = ('<div class="housing-rate-plot">'
              '<span class="housing-rate-benchmark-line benchmark-rent"></span>'
              '<span class="housing-rate-benchmark-line benchmark-school"></span>'
              '<span class="housing-rate-benchmark-line benchmark-cpi"></span>'
              '<span class="housing-rate-dot"')
if s.count(marker) == 10:
    s = s.replace(marker, line_spans)
elif s.count('class="housing-rate-benchmark-line benchmark-school"') != 10:
    raise SystemExit("Unexpected housing-rate row count while adding benchmark lines")

# Add all three BLS benchmarks to the context block while preserving the minimum-wage comparison.
s = s.replace('<div class="housing-rate-context-title">Wages &amp; inflation</div>',
              '<div class="housing-rate-context-title">Wages &amp; price benchmarks</div>', 1)

existing_cpi_item = '''        <div class="housing-rate-context-item">
          <div class="housing-rate-context-icon" aria-hidden="true">
            <svg viewBox="0 0 40 40">
              <g fill="currentColor">
                <rect x="6" y="25" width="6" height="9" rx="1"></rect>
                <rect x="17" y="18" width="6" height="16" rx="1"></rect>
                <rect x="28" y="9" width="6" height="25" rx="1"></rect>
              </g>
            </svg>
          </div>
          <div>
            <div class="housing-rate-context-label">U.S. consumer prices (all items, CPI)</div>
            <div class="housing-rate-context-metric"><strong>+3.4%</strong><span>July 2025 to July 2026</span></div>
            <div class="housing-rate-context-source">Source: <a href="https://www.bls.gov/news.release/cpi.htm" target="_blank" rel="noopener noreferrer">U.S. Bureau of Labor Statistics</a></div>
          </div>
        </div>'''
expanded_cpi_items = '''        <div class="housing-rate-context-item">
          <div>
            <div class="housing-rate-context-label">BLS lodging while at school</div>
            <div class="housing-rate-context-metric"><strong>+3.0%</strong><span>July 2025 to July 2026</span></div>
            <div class="housing-rate-context-source">Source: <a href="https://www.bls.gov/news.release/cpi.htm" target="_blank" rel="noopener noreferrer">U.S. Bureau of Labor Statistics</a> · <a href="https://www.bls.gov/cpi/additional-resources/entry-level-item-descriptions.htm" target="_blank" rel="noopener noreferrer">category definition</a></div>
          </div>
        </div>

        <div class="housing-rate-context-item">
          <div>
            <div class="housing-rate-context-label">BLS rent of primary residence</div>
            <div class="housing-rate-context-metric"><strong>+2.9%</strong><span>July 2025 to July 2026</span></div>
            <div class="housing-rate-context-source">Source: <a href="https://www.bls.gov/news.release/cpi.htm" target="_blank" rel="noopener noreferrer">U.S. Bureau of Labor Statistics</a></div>
          </div>
        </div>

''' + existing_cpi_item + '''
        <div class="housing-rate-context-note">BLS defines “lodging while at school” as college or university owned, leased or controlled housing. The BLS figures are national price benchmarks for context, not NC State-specific inflation rates.</div>'''
if existing_cpi_item in s and 'BLS lodging while at school' not in s:
    s = s.replace(existing_cpi_item, expanded_cpi_items, 1)
elif 'BLS lodging while at school' not in s:
    raise SystemExit("Could not find CPI context item")

# Make the second row of the two-column context block read cleanly on desktop.
context_css_anchor = '''.housing-rate-context-icon{
  display:none;
}
@media(max-width:700px){'''
context_css_new = '''.housing-rate-context-icon{
  display:none;
}
.housing-rate-context-item:nth-child(4),
.housing-rate-context-item:nth-child(5){
  margin-top:6px;
  padding-top:10px;
  border-top:1px solid var(--line);
}
.housing-rate-context-item:nth-child(4){
  padding-left:0;
  border-left:0;
}
.housing-rate-context-note{
  grid-column:1 / -1;
  margin-top:8px;
  padding-top:8px;
  border-top:1px solid var(--line);
  color:var(--muted);
  font-size:7.8px;
  line-height:1.35;
}
@media(max-width:700px){'''
if context_css_anchor in s:
    s = s.replace(context_css_anchor, context_css_new, 1)
elif '.housing-rate-context-note{' not in s:
    raise SystemExit("Could not find housing-rate context CSS anchor")

# Keep the benchmark legend readable on narrow screens.
mobile_anchor = '''  .housing-rate-axis-plot{
    grid-column:1 / -1;
    height:32px;
  }'''
mobile_new = '''  .housing-rate-benchmark-legend{
    gap:4px 9px;
    font-size:7.5px;
  }
  .housing-rate-benchmark-key{
    white-space:normal;
  }
  .housing-rate-axis-plot{
    grid-column:1 / -1;
    height:22px;
  }'''
if mobile_anchor in s:
    s = s.replace(mobile_anchor, mobile_new, 1)

p.write_text(s, encoding="utf-8")

# Expand the methodology/reference page with the same three BLS benchmarks and the school-lodging definition.
rp = Path("references.html")
r = rp.read_text(encoding="utf-8")

old_note = '''    <div class="use-note">
      <strong>Inflation context source:</strong> U.S. Bureau of Labor Statistics, Consumer Price Index — July 2026. The all-items CPI-U increased <strong>3.4%</strong> over the 12 months ending July 2026. <a href="https://www.bls.gov/news.release/cpi.htm" target="_blank" rel="noopener noreferrer">Official BLS CPI release</a>.
    </div>'''
new_note = '''    <div class="use-note">
      <strong>BLS price context:</strong> Over the 12 months ending July 2026, <strong>lodging while at school increased 3.0%</strong>, <strong>rent of primary residence increased 2.9%</strong>, and the <strong>all-items CPI-U increased 3.4%</strong>. <a href="https://www.bls.gov/news.release/cpi.htm" target="_blank" rel="noopener noreferrer">Official BLS CPI release</a>. BLS defines “lodging while at school” as housing owned, leased or controlled by a college or university, including eligible on- or off-campus housing. <a href="https://www.bls.gov/cpi/additional-resources/entry-level-item-descriptions.htm" target="_blank" rel="noopener noreferrer">BLS category definition</a>.
    </div>'''
if old_note in r:
    r = r.replace(old_note, new_note, 1)
elif 'lodging while at school increased 3.0%' not in r:
    raise SystemExit("Could not find old inflation context note in references.html")

reference16 = '''

<article class="ref" id="bls-housing-cpi-benchmarks">
  <div class="ref-head">
    <div>
      <div class="ref-no">Reference 16</div>
      <div class="ref-title">U.S. Bureau of Labor Statistics — Housing CPI Benchmarks</div>
    </div>
    <div class="tags">
      <span class="tag">Primary source</span>
      <span class="tag">BLS</span>
      <span class="tag">CPI</span>
      <span class="tag">Student housing</span>
    </div>
  </div>

  <div class="ref-body">
    <div class="meta-grid">
      <div class="meta-label">Organization</div>
      <div class="meta-value">U.S. Bureau of Labor Statistics</div>

      <div class="meta-label">Release</div>
      <div class="meta-value">Consumer Price Index — July 2026</div>

      <div class="meta-label">CPI source</div>
      <div class="meta-value"><a href="https://www.bls.gov/news.release/cpi.htm" target="_blank" rel="noopener noreferrer">Official BLS CPI release</a></div>

      <div class="meta-label">Category definition</div>
      <div class="meta-value"><a href="https://www.bls.gov/cpi/additional-resources/entry-level-item-descriptions.htm" target="_blank" rel="noopener noreferrer">BLS CPI entry-level item descriptions</a></div>

      <div class="meta-label">Accessed</div>
      <div class="meta-value">Sept. 11, 2026</div>

      <div class="meta-label">Source type</div>
      <div class="meta-value">Federal statistical release and CPI category documentation</div>
    </div>

    <hr class="rule">

    <h2>Benchmarks used in the article</h2>
    <div class="facts">
      <div class="fact">
        <div class="fact-label">Lodging while at school</div>
        <div class="fact-value"><strong>+3.0%</strong> from July 2025 to July 2026.</div>
      </div>
      <div class="fact">
        <div class="fact-label">Rent of primary residence</div>
        <div class="fact-value"><strong>+2.9%</strong> from July 2025 to July 2026.</div>
      </div>
      <div class="fact">
        <div class="fact-label">All items CPI-U</div>
        <div class="fact-value"><strong>+3.4%</strong> from July 2025 to July 2026.</div>
      </div>
      <div class="fact">
        <div class="fact-label">What “lodging while at school” means</div>
        <div class="fact-value">BLS includes rooms, apartments, flats and homes while at school when the housing is owned, leased or controlled by the college or university. Eligible housing can be on or off campus; privately owned housing qualifies only when it is subject to university or college regulations and price policies.</div>
      </div>
    </div>

    <div class="use-note">
      <strong>Article use:</strong> “Lodging while at school” is the closest national CPI comparison for NC State-controlled student housing, while “rent of primary residence” is the broader rental-housing comparison and all-items CPI shows general consumer-price inflation. These are national benchmarks and should not be described as NC State-specific inflation rates.
    </div>
  </div>
</article>
'''

insert_anchor = '''  </div>
</main>

<script>'''
if 'id="bls-housing-cpi-benchmarks"' not in r:
    if insert_anchor not in r:
        raise SystemExit("Could not find reference insertion anchor")
    r = r.replace(insert_anchor, reference16 + '\n  </div>\n</main>\n\n<script>', 1)

rp.write_text(r, encoding="utf-8")
