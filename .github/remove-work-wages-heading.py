from pathlib import Path

p = Path('draft-story-0915.html')
s = p.read_text(encoding='utf-8')

needle = """      const block=workGrid && workGrid.closest('section.block');
      if(!wrapper || !block) return;
"""
replacement = """      const block=workGrid && workGrid.closest('section.block');
      if(!wrapper || !block) return;
      const sectionLabel=block.querySelector('.section-label');
      if(sectionLabel) sectionLabel.style.display='none';
"""

if "sectionLabel=block.querySelector('.section-label')" not in s:
    if needle not in s:
        raise SystemExit('Could not find work-study embed block')
    s = s.replace(needle, replacement, 1)

# Cache-bust the embedded housing-rate panel so the draft immediately shows the
# current August 2026 BLS benchmarks and fixed September 11 release links.
s = s.replace(
    'id="housing-rate-frame" src="index.html"',
    'id="housing-rate-frame" src="index.html?v=20260915-august-bls"',
    1,
)

p.write_text(s, encoding='utf-8')
