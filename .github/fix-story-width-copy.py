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

p.write_text(s, encoding='utf-8')
