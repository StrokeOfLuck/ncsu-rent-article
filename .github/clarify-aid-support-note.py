from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')

old = '''<p class="aid-caution" id="preset-assumption">Each selection adds the full average award, assuming tuition and school fees are covered separately. Actual aid refunds may be smaller. Dividing by 12 gives a monthly equivalent, not a payment schedule. The averages describe different recipient groups; combining them is hypothetical. Loans must be repaid. <a href="references.html#aid-math">Aid assumptions</a></p>'''
new = '''<p class="aid-caution" id="preset-assumption">Each selection adds the full average award, assuming tuition and school fees are covered separately. Actual aid refunds may be smaller. Dividing by 12 gives a monthly equivalent, not a payment schedule. The averages describe different recipient groups; combining them is hypothetical. These examples show how additional financial support could reduce the share of a student’s available monthly resources going to housing. Loans must be repaid. <a href="references.html#aid-math">Aid assumptions</a></p>'''

if old not in s:
    raise SystemExit('Could not find aid caution text')

s = s.replace(old, new, 1)
p.write_text(s, encoding='utf-8')
