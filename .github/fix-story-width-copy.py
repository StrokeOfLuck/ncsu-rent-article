from pathlib import Path

p = Path('draft-story-0915.html')
s = p.read_text(encoding='utf-8')

# Let article copy align with the full width of the surrounding graphics instead of
# stopping at 820px and leaving a persistent empty column on the right.
s = s.replace(
    '''  .lede {\n    max-width:820px;''',
    '''  .lede {\n    max-width:none;\n    width:100%;''',
    1,
)
s = s.replace(
    '''  .story-copy {\n    max-width:820px;''',
    '''  .story-copy {\n    max-width:none;\n    width:100%;''',
    1,
)

old = '''    <p>While the Sept. 9 snapshot of listings from NC State’s Off-Campus Housing site found a lower mean advertised room rent than either residence-hall monthly equivalent shown above, utilities and additional fees vary by listing.</p>'''
new = '''    <p>While the Sept. 9 snapshot of listings from NC State’s Off-Campus Housing site found a lower mean advertised room rent than either residence-hall monthly equivalent shown above, the inclusion of utilities and additional fees varies by listing.</p>'''
if old in s:
    s = s.replace(old, new, 1)
elif new not in s:
    raise SystemExit('Could not find off-campus utilities sentence')

p.write_text(s, encoding='utf-8')
