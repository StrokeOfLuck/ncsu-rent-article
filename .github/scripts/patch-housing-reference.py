from pathlib import Path
import re

p = Path('references.html')
s = p.read_text(encoding='utf-8')

css_marker = '/* Residence hall range + rate-change chart */'
if css_marker not in s:
    css = r'''

/* Residence hall range + rate-change chart */
.range-source-grid {
  display:grid;
  grid-template-columns:repeat(2,minmax(0,1fr));
  gap:10px;
}
.range-source-card {
  border:1px solid var(--line);
  background:#fff;
  padding:11px 12px;
}
.range-source-card .range-kicker {
  color:var(--muted);
  font-size:9px;
  font-weight:800;
  letter-spacing:.08em;
  text-transform:uppercase;
}
.range-source-card .range-name {
  margin-top:5px;
  font-size:12px;
  font-weight:750;
  line-height:1.35;
}
.range-source-card .range-rate {
  margin-top:4px;
  font-size:12px;
  line-height:1.35;
}
.rate-change-chart {
  display:grid;
  gap:9px;
  margin-top:10px;
}
.rate-change-row {
  display:grid;
  grid-template-columns:minmax(245px, 1.45fr) minmax(180px, 1fr) 58px;
  gap:10px;
  align-items:center;
}
.rate-change-label {
  font-size:10.5px;
  line-height:1.3;
}
.rate-change-label strong {
  display:block;
  font-size:11px;
}
.rate-change-track {
  height:12px;
  overflow:hidden;
  border:1px solid var(--line);
  background:var(--soft);
}
.rate-change-bar {
  height:100%;
  background:var(--accent);
}
.rate-change-value {
  font-size:11px;
  font-weight:800;
  text-align:right;
  font-variant-numeric:tabular-nums;
}
@media(max-width:700px) {
  .range-source-grid { grid-template-columns:1fr; }
  .rate-change-row {
    grid-template-columns:1fr 46px;
    gap:5px 8px;
  }
  .rate-change-track {
    grid-column:1 / -1;
    grid-row:2;
  }
  .rate-change-value {
    grid-column:2;
    grid-row:1;
  }
}
'''
    s = s.replace('</style>', css + '\n</style>', 1)

replacement = '''    <h2>Projected 2026–27 range used for comparison</h2>
    <div class="range-source-grid">
      <div class="range-source-card">
        <div class="range-kicker">Lowest double*</div>
        <div class="range-name">Source row: Double</div>
        <div class="range-rate"><strong>$3,970</strong> projected per semester</div>
      </div>
      <div class="range-source-card">
        <div class="range-kicker">Highest double*</div>
        <div class="range-name">Source row: E.S. King — 1-bedroom undergraduate double</div>
        <div class="range-rate"><strong>$4,350</strong> projected per semester</div>
      </div>
      <div class="range-source-card">
        <div class="range-kicker">Lowest single</div>
        <div class="range-name">Source row: Coastal Quarters — single</div>
        <div class="range-rate"><strong>$4,350</strong> projected per semester</div>
      </div>
      <div class="range-source-card">
        <div class="range-kicker">Highest single</div>
        <div class="range-name">Source row: Single</div>
        <div class="range-rate"><strong>$4,600</strong> projected per semester</div>
      </div>
    </div>

    <div class="use-note">
      <strong>Article use:</strong> These four projected 2026–27 rows define the low and high ends of the double and single residence-hall comparison. Coastal Quarters carries an additional required $150 communication fee, which is included in its monthly-equivalent calculation below.
    </div>

    <hr class="rule">

    <h2>Step-by-step monthly equivalent math</h2>
    <div class="use-note">
      <strong>Method note:</strong> NC State lists these as semester charges, not monthly rent. For comparison, the projected room rate is combined with the required <strong>$150 ResNet fee</strong>, doubled for fall + spring, and divided by a <strong>9-month academic year</strong>. Coastal Quarters also adds its required <strong>$150 communication fee</strong> each semester. All figures are <strong>per student</strong>.
    </div>

    <div class="facts">
      <div class="fact">
        <div class="fact-label">Residence hall double*</div>
        <div class="fact-value">
          <strong>Low — Double:</strong> ($3,970 + $150) × 2 ÷ 9 = <strong>$915.56/month ≈ $916</strong><br>
          <strong>Calculated midpoint:</strong> (($3,970 + $4,350) ÷ 2 + $150) × 2 ÷ 9 = <strong>$957.78/month ≈ $958</strong><br>
          <strong>High — E.S. King 1-bedroom undergraduate double:</strong> ($4,350 + $150) × 2 ÷ 9 = <strong>$1,000/month</strong>
        </div>
      </div>

      <div class="fact">
        <div class="fact-label">Residence hall single</div>
        <div class="fact-value">
          <strong>Low — Coastal Quarters single:</strong> ($4,350 + $150 ResNet + $150 communication) × 2 ÷ 9 = <strong>$1,033.33/month ≈ $1,033</strong><br>
          <strong>Calculated midpoint:</strong> ($1,033.33 + $1,055.56) ÷ 2 = <strong>$1,044.45/month ≈ $1,044</strong><br>
          <strong>High — Single:</strong> ($4,600 + $150) × 2 ÷ 9 = <strong>$1,055.56/month ≈ $1,056</strong>
        </div>
      </div>
    </div>

    <div class="use-note">
      <strong>* Double means a shared room occupied by two students.</strong> Residence-hall rates are charged per student, not per room.
    </div>

    <hr class="rule">

    <h2>Projected rate increase from 2025–26 to 2026–27</h2>
    <div class="use-note">
      <strong>Calculation:</strong> (2026–27 projected room rate − 2025–26 room rate) ÷ 2025–26 room rate × 100. This chart compares the published <strong>room-rate rows only</strong>; ResNet and the Coastal Quarters communication fee are excluded so the year-to-year rate change is like-for-like.
    </div>

    <div class="rate-change-chart" aria-label="Projected percentage increase in NC State housing rates from 2025–26 to 2026–27">
      <div class="rate-change-row"><div class="rate-change-label"><strong>Single</strong>$4,275 → $4,600</div><div class="rate-change-track"><div class="rate-change-bar" style="width:95%"></div></div><div class="rate-change-value">7.60%</div></div>
      <div class="rate-change-row"><div class="rate-change-label"><strong>Wolf Village/Wolf Ridge — 1 bedroom/studio</strong>$5,000 → $5,375</div><div class="rate-change-track"><div class="rate-change-bar" style="width:93.75%"></div></div><div class="rate-change-value">7.50%</div></div>
      <div class="rate-change-row"><div class="rate-change-label"><strong>E.S. King/Western Manor — studio</strong>$3,900 → $4,150</div><div class="rate-change-track"><div class="rate-change-bar" style="width:80.13%"></div></div><div class="rate-change-value">6.41%</div></div>
      <div class="rate-change-row"><div class="rate-change-label"><strong>Wolf Village/Wolf Ridge — 2, 3 or 4 bedrooms</strong>$4,500 → $4,780</div><div class="rate-change-track"><div class="rate-change-bar" style="width:77.75%"></div></div><div class="rate-change-value">6.22%</div></div>
      <div class="rate-change-row"><div class="rate-change-label"><strong>E.S. King/Western Manor — 2 bedroom</strong>$5,000 → $5,300</div><div class="rate-change-track"><div class="rate-change-bar" style="width:75%"></div></div><div class="rate-change-value">6.00%</div></div>
      <div class="rate-change-row"><div class="rate-change-label"><strong>E.S. King — 1-bedroom undergraduate double</strong>$4,125 → $4,350</div><div class="rate-change-track"><div class="rate-change-bar" style="width:68.13%"></div></div><div class="rate-change-value">5.45%</div></div>
      <div class="rate-change-row"><div class="rate-change-label"><strong>E.S. King/Western Manor — 1 bedroom</strong>$4,375 → $4,600</div><div class="rate-change-track"><div class="rate-change-bar" style="width:64.38%"></div></div><div class="rate-change-value">5.14%</div></div>
      <div class="rate-change-row"><div class="rate-change-label"><strong>Double</strong>$3,800 → $3,970</div><div class="rate-change-track"><div class="rate-change-bar" style="width:55.88%"></div></div><div class="rate-change-value">4.47%</div></div>
      <div class="rate-change-row"><div class="rate-change-label"><strong>Coastal Quarters — single</strong>$4,225 → $4,350</div><div class="rate-change-track"><div class="rate-change-bar" style="width:37%"></div></div><div class="rate-change-value">2.96%</div></div>
      <div class="rate-change-row"><div class="rate-change-label"><strong>Coastal Quarters — double</strong>$3,950 → $4,025</div><div class="rate-change-track"><div class="rate-change-bar" style="width:23.75%"></div></div><div class="rate-change-value">1.90%</div></div>
    </div>

    <div class="use-note">
      The largest projected increase among the listed room-rate rows is the standard <strong>Single</strong> rate at <strong>7.60%</strong>; the smallest is the <strong>Coastal Quarters double</strong> at <strong>1.90%</strong>.
    </div>

    <hr class="rule">

    <h2>Saved evidence</h2>'''

pattern = re.compile(r'    <h2>Rates visible in saved evidence</h2>.*?    <h2>Saved evidence</h2>', re.S)
if not pattern.search(s):
    raise SystemExit('Housing rate section not found')
s = pattern.sub(replacement, s, count=1)
p.write_text(s, encoding='utf-8')
