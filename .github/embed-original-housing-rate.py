from pathlib import Path

p = Path("draft-story-0915.html")
s = p.read_text(encoding="utf-8")

marker = 'id="housing-rate-frame"'
if marker not in s:
    old = '''  <figure aria-label="NC State University Housing projected rate increases compared with inflation" style="margin:18px 0 0;">
    <img src="assets/housing-rate-increase-2025-26-to-2026-27.svg" alt="Chart showing projected NC State University Housing room-rate increases from 2025–26 to 2026–27. Eight of 10 listed housing options increase more than the 3.0% BLS lodging-while-at-school benchmark." style="display:block;width:100%;height:auto;">
  </figure>'''
    new = '''  <section class="housing-rate-original-embed" aria-label="NC State University Housing projected rate increases compared with inflation">
    <iframe id="housing-rate-frame" src="index.html" title="University Housing rate increase from 2025–26 to 2026–27, with wages and price benchmarks" loading="lazy"></iframe>
  </section>'''
    if old not in s:
        raise SystemExit("Could not find static housing-rate figure in draft")
    s = s.replace(old, new, 1)

css_marker = "/* Original University Housing rate panel embed */"
if css_marker not in s:
    css = r'''

/* Original University Housing rate panel embed */
.housing-rate-original-embed{
  margin:18px 0 0;
}
.housing-rate-original-embed iframe{
  display:block;
  width:100%;
  min-height:520px;
  border:0;
  background:#fff;
}
/* End original University Housing rate panel embed */
'''
    s = s.replace('</style>', css + '\n</style>', 1)

js_marker = "// Reuse the original University Housing rate panel 1:1 from index.html."
if js_marker not in s:
    js = r'''

// Reuse the original University Housing rate panel 1:1 from index.html.
(function(){
  const frame=document.getElementById('housing-rate-frame');
  if(!frame) return;

  function trimHousingRate(){
    try {
      const d=frame.contentDocument;
      if(!d) return;
      const wrapper=d.querySelector('.wrapper');
      const block=d.querySelector('.housing-rate-change-block');
      if(!wrapper || !block) return;

      [...wrapper.children].forEach(el => {
        el.style.display = el===block ? '' : 'none';
      });

      wrapper.style.width='100%';
      wrapper.style.maxWidth='none';
      wrapper.style.margin='0';
      wrapper.style.padding='0';
      block.style.margin='0';
      block.style.paddingTop='0';
      block.style.borderTop='0';
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

  frame.addEventListener('load',trimHousingRate);
})();
'''
    s = s.replace('</script>', js + '\n</script>', 1)

p.write_text(s, encoding="utf-8")
