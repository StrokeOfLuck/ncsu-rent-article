from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')

# Keep the published summary visually checkable without changing the underlying
# listing-level analysis. The low/high range is displayed after rounding each
# endpoint to a whole dollar, so calculate the adjacent displayed midpoint from
# those same visible endpoints. Raw/unrounded stats remain unchanged everywhere
# else, including the affordability analysis and audit math.
old_label = '<div class="room-overall-line"><span>Mean advertised room rent <strong id="combinedPerMid">$0</strong></span></div>'
new_label = '<div class="room-overall-line"><span>Midpoint of displayed mean range <strong id="combinedPerMid">$0</strong></span></div>'
if old_label in s:
    s = s.replace(old_label, new_label, 1)
elif new_label not in s:
    raise SystemExit('Could not find room midpoint display label')

old_note = 'Monthly prices. The range averages listings’ low and high prices separately. The mean averages each listing’s midpoint, with one vote per listing. Utilities and fees vary.'
new_note = 'Monthly prices. The low–high range is rounded to whole dollars. The displayed midpoint is calculated from those rounded figures so the visible arithmetic checks. Underlying analysis still uses unrounded listing values, with one vote per listing. Utilities and fees vary.'
if old_note in s:
    s = s.replace(old_note, new_note, 1)
elif new_note not in s:
    raise SystemExit('Could not find room summary method note')

old_display = """  for(const [name,stats] of [['Per',local.perOverall]]) {
    document.getElementById('combined'+name+'Overall').textContent=stats.display;
    document.getElementById('combined'+name+'Mid').textContent=money(stats.midpoint);
  }"""
new_display = """  for(const [name,stats] of [['Per',local.perOverall]]) {
    document.getElementById('combined'+name+'Overall').textContent=stats.display;
    const displayedLow=Math.round(stats.avg_low);
    const displayedHigh=Math.round(stats.avg_high);
    const displayedMid=(displayedLow+displayedHigh)/2;
    const displayedMidText=Number.isInteger(displayedMid)
      ? '$'+displayedMid.toLocaleString('en-US')
      : '$'+displayedMid.toLocaleString('en-US',{minimumFractionDigits:2,maximumFractionDigits:2});
    document.getElementById('combined'+name+'Mid').textContent=displayedMidText;
  }"""
if old_display in s:
    s = s.replace(old_display, new_display, 1)
elif 'const displayedMid=(displayedLow+displayedHigh)/2;' not in s:
    raise SystemExit('Could not find combined room midpoint display block')

p.write_text(s, encoding='utf-8')
