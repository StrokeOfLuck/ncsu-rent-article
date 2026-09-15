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

# Add the wages transition and reuse the existing interactive work-study block from
# index.html rather than maintaining a second copy of the same graphic.
if 'id="work-wages-frame"' not in s:
    marker = '''  <div class="continue">Continue drafting here…</div>'''
    insert = '''  <section class="story-copy" aria-label="Student wages and Federal Work-Study">
    <p>As prices rise, students have to stretch each dollar further. <a href="https://www.labor.nc.gov/workplace-rights/employee-rights-regarding-time-worked-and-wages-earned/minimum-wage-nc" target="_blank" rel="noopener noreferrer">North Carolina’s minimum wage has remained $7.25 an hour since July 2009.</a> <a href="https://emas.ncsu.edu/employment/federal-work-study-program/" target="_blank" rel="noopener noreferrer">NC State’s Federal Work-Study program</a> lists an allowable wage range of $7.25 to $15 an hour, with higher wages requiring a case-by-case exception.</p>
  </section>

  <section class="work-wages-original-embed" aria-label="Illustrative student work earnings at selected hours">
    <iframe id="work-wages-frame" src="index.html" title="Illustrative gross earnings and Federal Work-Study hours" loading="lazy"></iframe>
  </section>

  <div class="continue">Continue drafting here…</div>'''
    if marker not in s:
        raise SystemExit('Could not find continue marker for wages section')
    s = s.replace(marker, insert, 1)

css_marker = '/* Original work-study wages panel embed */'
if css_marker not in s:
    css = r'''

/* Original work-study wages panel embed */
.work-wages-original-embed{
  margin:10px 0 0;
}
.work-wages-original-embed iframe{
  display:block;
  width:100%;
  min-height:260px;
  border:0;
  background:#fff;
}
/* End original work-study wages panel embed */
'''
    s = s.replace('</style>', css + '\n</style>', 1)

js_marker = '// Reuse the original work-study earnings block 1:1 from index.html.'
if js_marker not in s:
    js = r'''

// Reuse the original work-study earnings block 1:1 from index.html.
(function(){
  const frame=document.getElementById('work-wages-frame');
  if(!frame) return;

  function trimWorkWages(){
    try {
      const d=frame.contentDocument;
      if(!d) return;
      const wrapper=d.querySelector('.wrapper');
      const workGrid=d.querySelector('.work-grid.clean-work-grid');
      const block=workGrid && workGrid.closest('section.block');
      if(!wrapper || !block) return;

      [...wrapper.children].forEach(el => {
        el.style.display = el===block ? '' : 'none';
      });

      wrapper.style.width='100%';
      wrapper.style.maxWidth='none';
      wrapper.style.margin='0';
      wrapper.style.padding='0';
      block.style.margin='0';
      d.documentElement.style.background='#fff';
      d.body.style.margin='0';
      d.body.style.background='#fff';

      const resize=()=>{
        frame.style.height=Math.ceil(block.getBoundingClientRect().height+4)+'px';
      };
      resize();
      setTimeout(resize,250);
      setTimeout(resize,900);
      if(frame.contentWindow.ResizeObserver){
        const ro=new frame.contentWindow.ResizeObserver(resize);
        ro.observe(block);
      }
    } catch(e) {
      // Same-origin GitHub Pages embed should allow trimming; otherwise leave source page intact.
    }
  }

  frame.addEventListener('load',trimWorkWages);
})();
'''
    s = s.replace('</script>', js + '\n</script>', 1)

# Default the comparison to room charges only. ResNet remains a required separate
# cost and can be added with the checkbox.
s = s.replace(
    '''Projected 2026–27 residence hall rates from official housing rates, converted from two semester charges to a 9-month academic-year monthly equivalent. By default, the calculation includes the required $150-per-semester ResNet fee, which residents pay for internet access but which goes to OIT, not University Housing. Use the ResNet toggle below to view the room charge alone; residents still pay the required fee.''',
    '''Projected 2026–27 residence hall rates from official housing rates, converted from two semester charges to a 9-month academic-year monthly equivalent. By default, the comparison shows the University Housing room charge alone. Residents also pay a required $150-per-semester ResNet fee for internet access, which goes to OIT rather than University Housing; use the ResNet checkbox below to add it.''',
    1,
)
s = s.replace('id="resnet-fee" checked', 'id="resnet-fee"', 1)
s = s.replace('≈ $916/month', '≈ $882/month', 1)
s = s.replace('≈ $1,056/month', '≈ $1,022/month', 1)

old_options = '''    <div class="break-option">\n      <input type="checkbox" id="winter-break">\n      <label for="winter-break">\n        <strong>Include a full winter-break stay</strong>\n        <span class="break-note">Uses NC State’s 2025–26 full-break rate of $360 ($15/night). The 2026–27 winter-break charge and dates have not yet been posted, so this is a reference scenario.</span>\n      </label>\n    </div>\n\n    <div class="break-option resnet-option">\n      <input type="checkbox" id="resnet-fee">\n      <label for="resnet-fee">\n        <strong>Include required ResNet fee (+$150/semester)</strong>\n        <span class="break-note">Checked by default because residents pay this separate OIT charge for internet access. Turn it off only to compare University Housing room charges without the internet fee.</span>\n      </label>\n    </div>'''
new_options = '''    <div class="comparison-options">\n      <div class="break-option">\n        <input type="checkbox" id="winter-break">\n        <label for="winter-break"><strong>Full winter break (+$360)</strong> <span class="break-note">2025–26 reference rate; 2026–27 rate not yet posted.</span></label>\n      </div>\n\n      <div class="break-option resnet-option">\n        <input type="checkbox" id="resnet-fee">\n        <label for="resnet-fee"><strong>Required ResNet (+$150/semester; ≈ +$33/month)</strong> <span class="break-note">Paid to OIT for internet access.</span></label>\n      </div>\n    </div>'''
if old_options in s:
    s = s.replace(old_options, new_options, 1)
elif 'class="comparison-options"' not in s:
    raise SystemExit('Could not find housing comparison options')

if '/* Compact comparison options */' not in s:
    compact_css = r'''

/* Compact comparison options */
.comparison-options{
  display:grid;
  grid-template-columns:1fr 1fr;
  gap:10px;
  margin:1px 0 12px;
}
.comparison-options .break-option{
  margin:0;
  padding:9px 10px;
  border:1px solid var(--line);
  align-items:center;
}
.comparison-options .break-option + .break-option{
  margin-top:0;
  border-top:1px solid var(--line);
}
.comparison-options .break-note{
  display:inline;
  margin:0 0 0 5px;
}
@media (max-width:700px){
  .comparison-options{ grid-template-columns:1fr; gap:6px; }
  .comparison-options .break-note{ display:block; margin:2px 0 0; }
}
/* End compact comparison options */
'''
    s = s.replace('</style>', compact_css + '\n</style>', 1)

# The iframe is resized by JS after load. The 520px minimum prevented it from
# shrinking to the embedded panel's actual height and created a large white gap.
s = s.replace('''  min-height:520px;\n  border:0;''', '''  min-height:0;\n  border:0;''', 1)

p.write_text(s, encoding='utf-8')
