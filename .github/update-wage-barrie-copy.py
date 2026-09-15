from pathlib import Path
import re

p = Path('draft-story-0915.html')
s = p.read_text(encoding='utf-8')

wage_section = '''  <section class="story-copy" aria-label="Student wages and Federal Work-Study">
    <p>As prices rise, students have to stretch each dollar further. <a href="https://www.dol.gov/agencies/whd/minimum-wage/history/chart" target="_blank" rel="noopener noreferrer">North Carolina’s minimum wage has remained $7.25 an hour since July 2009.</a> <a href="https://emas.ncsu.edu/employment/federal-work-study-program/" target="_blank" rel="noopener noreferrer">NC State’s Federal Work-Study program</a> lists an allowable wage range of $7.25 to $15 an hour, with higher wages requiring a case-by-case exception. The university says work-study students generally should work no more than 20 hours per week, although they may hold another non-work-study job at the same time.</p>
  </section>'''

s, n = re.subn(
    r'  <section class="story-copy" aria-label="Student wages and Federal Work-Study">\s*<p>.*?</p>\s*</section>',
    wage_section,
    s,
    count=1,
    flags=re.S,
)
if n != 1:
    raise SystemExit('Could not replace student wages section')

work_embed = '''  <section class="work-wages-original-embed" aria-label="Illustrative student work earnings at selected hours">
    <iframe id="work-wages-frame" src="index.html" title="Illustrative gross earnings and Federal Work-Study hours" loading="lazy"></iframe>
  </section>'''

barrie = work_embed + '''

  <section class="story-copy" aria-label="Student work hours and academic pressure">
    <p>Professor Barrie said he often asks students who are struggling in studio how much they are working and whether they can afford to cut back.</p>

    <blockquote>“I’ll say, ‘So how much are you working?’ And they’ll tell me, and I’ll say, ‘Do you need to work that much?’ And then often the answer is, ‘I do.’”</blockquote>

    <p>For those students, Barrie said, the answer is to take that financial reality “at face value” and work with it.</p>
  </section>'''

s, n = re.subn(
    re.escape(work_embed) + r'\s*<section class="story-copy" aria-label="Student work hours and academic pressure">.*?</section>',
    barrie,
    s,
    count=1,
    flags=re.S,
)
if n == 0:
    if work_embed not in s:
        raise SystemExit('Could not find work wages embed for Barrie insertion')
    s = s.replace(work_embed, barrie, 1)

p.write_text(s, encoding='utf-8')
