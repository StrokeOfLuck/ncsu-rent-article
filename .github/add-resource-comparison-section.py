from pathlib import Path

p = Path('draft-story-0915.html')
s = p.read_text(encoding='utf-8')

marker = '  <div class="continue">Continue drafting here…</div>'
section_marker = 'id="resources-frame"'

if section_marker not in s:
    insert = '''  <section class="story-copy" aria-label="Room rent and student monthly resources">
    <p>To compare advertised room rents with the resources available to a working student, this analysis uses <a href="references.html#hud-30-percent">HUD’s 30% housing cost-burden threshold</a> as a reference point. HUD considers households spending more than 30% of their income on housing cost burdened and says they may have difficulty affording other necessities such as food, clothing, transportation, and medical care.</p>

    <p>The interactive comparison uses wages ranging from North Carolina’s $7.25 minimum wage to $15 an hour and allows readers to add NC State’s reported average need-based grant or need-based loan award. Because grants and loans are not the same as household income, the 30% line is a reference rather than a formal HUD cost-burden determination.</p>

    <p>At $15 an hour and 40 hours a week, the $862 mean advertised Main Campus room rent still equals about <strong>33% of gross wages</strong> with no aid selected. Adding the average need-based loan lowers the illustrative share to about <strong>29%</strong>, while adding the average need-based grant lowers it to about <strong>23%</strong>. In both cases, getting below the 30% reference requires adding financial aid to wages.</p>
  </section>

  <section class="resources-original-embed" aria-label="How room rent compares with a student’s monthly resources">
    <iframe id="resources-frame" src="index.html" title="How does room rent compare with a student’s monthly resources?" loading="lazy"></iframe>
  </section>

''' + marker
    if marker not in s:
        raise SystemExit('Could not find continue marker for resource comparison section')
    s = s.replace(marker, insert, 1)

css_marker = '/* Monthly resources comparison embed */'
if css_marker not in s:
    css = r'''

/* Monthly resources comparison embed */
.resources-original-embed{
  margin:18px 0 0;
}
.resources-original-embed iframe{
  display:block;
  width:100%;
  min-height:0;
  border:0;
  background:#fff;
}
/* End monthly resources comparison embed */
'''
    s = s.replace('</style>', css + '\n</style>', 1)

js_marker = '// Reuse the original monthly-resources affordability block 1:1 from index.html.'
if js_marker not in s:
    js = r'''

// Reuse the original monthly-resources affordability block 1:1 from index.html.
(function(){
  const frame=document.getElementById('resources-frame');
  if(!frame) return;

  function trimResources(){
    try {
      const d=frame.contentDocument;
      if(!d) return;
      const wrapper=d.querySelector('.wrapper');
      let block=d.querySelector('.affordability-block');
      if(!block){
        const candidates=[...d.querySelectorAll('section.block, section, .block')];
        block=candidates.find(el => /HOW DOES ROOM RENT COMPARE WITH A STUDENT.?S MONTHLY RESOURCES/i.test(el.textContent || '')) ||
              candidates.find(el => /Compare with need-based aid/i.test(el.textContent || ''));
      }
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

  frame.addEventListener('load',trimResources);
})();
'''
    s = s.replace('</script>', js + '\n</script>', 1)

p.write_text(s, encoding='utf-8')
