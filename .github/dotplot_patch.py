from pathlib import Path
import re

p = Path("index.html")
s = p.read_text(encoding="utf-8")

# This patch is intentionally idempotent. Once the interactive controls exist,
# a later workflow run can safely leave the reader-facing file unchanged.
if 'housing-rate-benchmark-control' not in s:
    # Remove the three-line legend above the dot plot. The selected benchmark is
    # labeled directly on the chart instead.
    s, removed = re.subn(
        r'\n\s*<div class="housing-rate-benchmark-legend"[^>]*>.*?</div>\n(\s*<div class="housing-rate-axis")',
        r'\n\1',
        s,
        count=1,
        flags=re.S,
    )
    if removed != 1:
        raise SystemExit("Could not find the BLS benchmark legend")

    # Default to the BLS student-housing measure because this chart is comparing
    # NC State-controlled housing rates. Users can hover/focus/tap the other BLS
    # measures to swap the reference line.
    s = s.replace(
        '<div class="housing-rate-chart" aria-label="Projected percentage increase in NC State housing rates from 2025–26 to 2026–27. Dots show each housing rate increase on a zero to eight percent scale. Vertical reference lines show July 2026 BLS 12-month changes for rent of primary residence at 2.9 percent, lodging while at school at 3.0 percent, and all-items CPI at 3.4 percent.">',
        '<div class="housing-rate-chart" data-benchmark="school" aria-label="Projected percentage increase in NC State housing rates from 2025–26 to 2026–27. Dots show each housing rate increase on a zero to eight percent scale. An interactive vertical reference line compares the housing-rate changes with July 2026 BLS 12-month price benchmarks.">',
        1,
    )

    axis_open = '''          <div class="housing-rate-axis-plot">\n            <span class="housing-rate-axis-tick first" style="left:0%">0%</span>'''
    axis_new = '''          <div class="housing-rate-axis-plot">\n            <span id="housing-rate-active-label" class="housing-rate-active-label" style="left:37.5%">Lodging while at school 3.0%</span>\n            <span class="housing-rate-axis-tick first" style="left:0%">0%</span>'''
    if axis_open not in s:
        raise SystemExit("Could not find housing rate axis")
    s = s.replace(axis_open, axis_new, 1)

    # The dynamic benchmark label occupies the middle of the scale, so remove the
    # redundant 4% tick. The 0, 2, 6 and 8 percent ticks still make the scale clear.
    s = s.replace(
        '            <span class="housing-rate-axis-tick" style="left:50%">4%</span>\n',
        '',
        1,
    )

    def mark_control(html, label, key, aria):
        pattern = (
            r'<div class="housing-rate-context-item">'
            r'(?=(?:(?!<div class="housing-rate-context-item">).)*?'
            r'<div class="housing-rate-context-label">' + re.escape(label) + r'</div>)'
        )
        replacement = (
            '<div class="housing-rate-context-item housing-rate-benchmark-control" '
            f'data-benchmark="{key}" tabindex="0" aria-label="{aria}">'
        )
        updated, count = re.subn(pattern, replacement, html, count=1, flags=re.S)
        if count != 1:
            raise SystemExit(f"Could not mark benchmark control: {label}")
        return updated

    s = mark_control(
        s,
        'BLS lodging while at school',
        'school',
        'Show BLS lodging while at school, 3.0 percent, on the chart',
    )
    s = mark_control(
        s,
        'BLS rent of primary residence',
        'rent',
        'Show BLS rent of primary residence, 2.9 percent, on the chart',
    )
    s = mark_control(
        s,
        'U.S. consumer prices (all items, CPI)',
        'cpi',
        'Show all-items CPI, 3.4 percent, on the chart',
    )

    # Add the interaction/one-row layout as a final CSS override so it does not
    # disturb the rest of the existing article styles.
    css = r'''

/* Interactive BLS housing benchmark selector */
.housing-rate-benchmark-legend{
  display:none !important;
}
.housing-rate-axis-plot{
  height:32px;
}
.housing-rate-active-label{
  position:absolute;
  top:0;
  transform:translateX(-50%);
  color:#6fb4f2;
  font-size:8.5px;
  line-height:1;
  font-weight:900;
  white-space:nowrap;
  z-index:3;
  transition:left .16s ease;
}
.housing-rate-active-label::after{
  content:"";
  position:absolute;
  left:50%;
  top:13px;
  height:27px;
  border-left:2px solid #6fb4f2;
  opacity:.95;
}
.housing-rate-benchmark-line{
  display:none !important;
  border-left:2px solid #6fb4f2 !important;
  opacity:.95 !important;
}
.housing-rate-chart[data-benchmark="school"] .benchmark-school,
.housing-rate-chart[data-benchmark="rent"] .benchmark-rent,
.housing-rate-chart[data-benchmark="cpi"] .benchmark-cpi{
  display:block !important;
}

.housing-rate-context{
  grid-template-columns:repeat(4,minmax(0,1fr));
  align-items:stretch;
}
.housing-rate-context-title{
  grid-column:1 / -1;
}
.housing-rate-context > .housing-rate-context-item{
  min-width:0;
  margin-top:0 !important;
  padding:10px 14px 6px !important;
  border-top:0 !important;
}
.housing-rate-context > .housing-rate-context-title + .housing-rate-context-item{
  padding-left:0 !important;
  border-left:0 !important;
}
.housing-rate-context > .housing-rate-context-item:nth-child(4),
.housing-rate-context > .housing-rate-context-item:nth-child(5){
  padding-left:14px !important;
  border-left:1px solid var(--line) !important;
}
.housing-rate-benchmark-control{
  position:relative;
  cursor:pointer;
  background:rgba(43,95,151,.035);
  transition:background .14s ease, box-shadow .14s ease;
}
.housing-rate-benchmark-control::before{
  content:"";
  position:absolute;
  left:14px;
  right:14px;
  top:0;
  height:2px;
  background:var(--blue);
  opacity:.18;
}
.housing-rate-benchmark-control:hover,
.housing-rate-benchmark-control:focus-visible{
  outline:none;
  background:rgba(43,95,151,.075);
}
.housing-rate-benchmark-control.is-active{
  background:rgba(43,95,151,.095);
  box-shadow:inset 0 2px 0 var(--blue);
}
.housing-rate-benchmark-control.is-active::before{
  opacity:0;
}
.housing-rate-context-note{
  grid-column:1 / -1;
}

@media(max-width:900px){
  .housing-rate-context{
    grid-template-columns:repeat(2,minmax(0,1fr));
  }
  .housing-rate-context > .housing-rate-context-item{
    border-top:1px solid var(--line) !important;
  }
  .housing-rate-context > .housing-rate-context-item:nth-child(2),
  .housing-rate-context > .housing-rate-context-item:nth-child(4){
    border-left:0 !important;
    padding-left:0 !important;
  }
  .housing-rate-context > .housing-rate-context-item:nth-child(3),
  .housing-rate-context > .housing-rate-context-item:nth-child(5){
    border-left:1px solid var(--line) !important;
    padding-left:14px !important;
  }
}

@media(max-width:700px){
  .housing-rate-active-label{
    font-size:7.6px;
  }
  .housing-rate-context{
    grid-template-columns:1fr;
  }
  .housing-rate-context > .housing-rate-context-item,
  .housing-rate-context > .housing-rate-context-item:nth-child(2),
  .housing-rate-context > .housing-rate-context-item:nth-child(3),
  .housing-rate-context > .housing-rate-context-item:nth-child(4),
  .housing-rate-context > .housing-rate-context-item:nth-child(5){
    padding:9px 0 !important;
    border-left:0 !important;
    border-top:1px solid var(--line) !important;
  }
  .housing-rate-benchmark-control::before{
    left:0;
    right:0;
  }
}
/* End interactive BLS housing benchmark selector */
'''
    if '</style>' not in s:
        raise SystemExit("Could not find closing style tag")
    s = s.replace('</style>', css + '\n</style>', 1)

    # Hover/focus temporarily previews a benchmark. Clicking/tapping pins it.
    # Leaving a hover returns to the pinned benchmark. The default is the school
    # lodging index because the plotted NC State rates are university housing.
    js = r'''
<script>
(() => {
  const chart = document.querySelector('.housing-rate-chart');
  const label = document.getElementById('housing-rate-active-label');
  const controls = [...document.querySelectorAll('.housing-rate-benchmark-control')];
  if (!chart || !label || !controls.length) return;

  const benchmarks = {
    school: { label: 'Lodging while at school 3.0%', left: '37.5%' },
    rent:   { label: 'Rent of primary residence 2.9%', left: '36.25%' },
    cpi:    { label: 'All items CPI 3.4%', left: '42.5%' }
  };

  let pinned = 'school';

  const show = key => {
    const benchmark = benchmarks[key] || benchmarks.school;
    chart.dataset.benchmark = key in benchmarks ? key : 'school';
    label.textContent = benchmark.label;
    label.style.left = benchmark.left;
    controls.forEach(control => {
      control.classList.toggle('is-active', control.dataset.benchmark === chart.dataset.benchmark);
    });
  };

  controls.forEach(control => {
    const key = control.dataset.benchmark;
    control.addEventListener('mouseenter', () => show(key));
    control.addEventListener('mouseleave', () => show(pinned));
    control.addEventListener('focus', () => show(key));
    control.addEventListener('blur', () => show(pinned));
    control.addEventListener('click', event => {
      if (event.target.closest('a')) return;
      pinned = key;
      show(key);
    });
    control.addEventListener('keydown', event => {
      if (event.key === 'Enter' || event.key === ' ') {
        event.preventDefault();
        pinned = key;
        show(key);
      }
    });
  });

  show(pinned);
})();
</script>
'''
    if '</body>' not in s:
        raise SystemExit("Could not find closing body tag")
    s = s.replace('</body>', js + '\n</body>', 1)

    p.write_text(s, encoding="utf-8")
else:
    print("Interactive BLS benchmark selector already present; no changes needed.")
