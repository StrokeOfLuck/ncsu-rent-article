from pathlib import Path
import re

# Move the room-listing workbook link out of the $862 note and onto the same
# utility row as the winter-break control, aligned on the right.

# Story draft / embedded comparison.
p = Path('draft-story-0915.html')
s = p.read_text(encoding='utf-8')

s = s.replace(
    '<a href="references.html#rental-method">How this is calculated</a> · <a href="references.html#room-rent-audit">Room-listing Excel audit</a>',
    '<a href="references.html#rental-method">How this is calculated</a>',
)

# Make the embedded utility row a left/right flex row.
old_class = "          breakRow.className='draft-campus-break-row';"
new_class = """          breakRow.className='draft-campus-break-row';
          breakRow.style.display='flex';
          breakRow.style.alignItems='center';
          breakRow.style.justifyContent='space-between';
          breakRow.style.gap='12px';"""
if old_class in s and "breakRow.style.justifyContent='space-between';" not in s:
    s = s.replace(old_class, new_class, 1)

# Add the audit link as the right-hand item on that row.
if 'class="draft-room-audit-link"' not in s:
    s = re.sub(
        r"(breakRow\.innerHTML='<div class=\"draft-campus-break-control\">.*?</div>)(';)",
        r'\1<a class="draft-room-audit-link" href="references.html#room-rent-audit" style="margin-left:auto;white-space:nowrap;font-size:9px;">Room-listing Excel audit</a>\2',
        s,
        count=1,
    )

if 'class="draft-room-audit-link"' not in s:
    raise SystemExit('Could not add room audit link to embedded winter-break row')

p.write_text(s, encoding='utf-8')

# Standalone interactive page.
p = Path('index.html')
s = p.read_text(encoding='utf-8')

s = s.replace(
    '<a href="references.html#rental-method">How this is calculated</a> · <a href="references.html#room-rent-audit">Room-listing Excel audit</a>',
    '<a href="references.html#rental-method">How this is calculated</a>',
)

# Two columns: winter-break control on the left, workbook link on the right.
s = re.sub(
    r'(\.main-campus-comparison-options\{\s*display:grid;\s*grid-template-columns:)1fr(;)',
    r'\1minmax(0,1fr) auto\2',
    s,
    count=1,
)
if '.main-campus-comparison-options{' in s and 'align-items:center;' not in s[s.find('.main-campus-comparison-options{'):s.find('.main-campus-comparison-options{')+220]:
    s = s.replace(
        '.main-campus-comparison-options{\n  display:grid;\n  grid-template-columns:minmax(0,1fr) auto;\n  gap:12px;',
        '.main-campus-comparison-options{\n  display:grid;\n  grid-template-columns:minmax(0,1fr) auto;\n  gap:12px;\n  align-items:center;',
        1,
    )

if 'class="room-audit-utility-link"' not in s:
    old = '''            <div class="main-campus-option">
              <input type="checkbox" id="main-winter-break">
              <label for="main-winter-break"><strong>Full winter break (+$360)</strong><span>2025–26 reference rate; 2026–27 rate not yet posted.</span></label>
            </div>
          </div>'''
    new = '''            <div class="main-campus-option">
              <input type="checkbox" id="main-winter-break">
              <label for="main-winter-break"><strong>Full winter break (+$360)</strong><span>2025–26 reference rate; 2026–27 rate not yet posted.</span></label>
            </div>
            <a class="room-audit-utility-link" href="references.html#room-rent-audit" style="justify-self:end;white-space:nowrap;font-size:10px;">Room-listing Excel audit</a>
          </div>'''
    if old not in s:
        raise SystemExit('Could not find standalone winter-break utility row')
    s = s.replace(old, new, 1)

if 'class="room-audit-utility-link"' not in s:
    raise SystemExit('Could not add standalone room audit utility link')

p.write_text(s, encoding='utf-8')
