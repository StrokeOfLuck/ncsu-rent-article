from pathlib import Path
import re

# Keep the standalone interactive page's aid explanation current.
p = Path('index.html')
s = p.read_text(encoding='utf-8')

old = '''<p class="aid-caution" id="preset-assumption">Each selection adds the full average award, assuming tuition and school fees are covered separately. Actual aid refunds may be smaller. Dividing by 12 gives a monthly equivalent, not a payment schedule. The averages describe different recipient groups; combining them is hypothetical. Loans must be repaid. <a href="references.html#aid-math">Aid assumptions</a></p>'''
new = '''<p class="aid-caution" id="preset-assumption">Each selection adds the full average award, assuming tuition and school fees are covered separately. Actual aid refunds may be smaller. Dividing by 12 gives a monthly equivalent, not a payment schedule. The averages describe different recipient groups; combining them is hypothetical. These examples show how additional financial support could reduce the share of a student’s available monthly resources going to housing. Loans must be repaid. <a href="references.html#aid-math">Aid assumptions</a></p>'''

if old in s:
    s = s.replace(old, new, 1)
elif new not in s:
    raise SystemExit('Could not find aid caution text')

p.write_text(s, encoding='utf-8')

# The article draft embeds index.html. Bust the iframe cache so the article shows
# the same updated aid explanation immediately instead of a stale copy.
p = Path('draft-story-0915.html')
s = p.read_text(encoding='utf-8')
updated, count = re.subn(
    r'src="index\.html(?:\?v=[^"]*)?#map"',
    'src="index.html?v=20260916-aid-support#map"',
    s,
    count=1,
)
if count != 1:
    raise SystemExit('Could not find article index.html iframe')
p.write_text(updated, encoding='utf-8')
