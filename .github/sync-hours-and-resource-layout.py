from pathlib import Path

p = Path('draft-story-0915.html')
s = p.read_text(encoding='utf-8')

# The draft iframe is narrower than the standalone analysis page, so index.html's
# <=980px media query stacks the two monthly-resource cards. For the draft, keep
# them side by side until the true mobile breakpoint.
layout_marker = """      d.body.style.background='#fff';

      const resize=()=>{
        frame.style.height=Math.ceil(block.getBoundingClientRect().height+4)+'px';
      };"""
layout_replacement = """      d.body.style.background='#fff';

      if(!d.getElementById('draft-resources-layout-style')){
        const style=d.createElement('style');
        style.id='draft-resources-layout-style';
        style.textContent=`
          @media (min-width:701px){
            .burden-grid{
              grid-template-columns:19fr 20fr !important;
            }
          }
        `;
        d.head.appendChild(style);
      }

      const resize=()=>{
        frame.style.height=Math.ceil(block.getBoundingClientRect().height+4)+'px';
      };"""

# Only replace the occurrence inside trimResources, not the other iframe trimmers.
resources_start = s.find('// Reuse the original monthly-resources affordability block 1:1 from index.html.')
if resources_start < 0:
    raise SystemExit('Could not find monthly resources embed script')
head = s[:resources_start]
tail = s[resources_start:]
if "draft-resources-layout-style" not in tail:
    if layout_marker not in tail:
        raise SystemExit('Could not find resources layout insertion point')
    tail = tail.replace(layout_marker, layout_replacement, 1)
s = head + tail

# Keep the earlier work-hours slider and both affordability-card hour sliders in sync.
# This is draft-only behavior across the two same-origin embedded copies of index.html.
sync_marker = '// Sync all visible hour sliders across the work and affordability embeds.'
if sync_marker not in s:
    sync_js = r'''

// Sync all visible hour sliders across the work and affordability embeds.
(function(){
  const workFrame=document.getElementById('work-wages-frame');
  const resourcesFrame=document.getElementById('resources-frame');
  if(!workFrame || !resourcesFrame) return;

  let syncing=false;

  function hourSliders(){
    const out=[];
    try {
      const d=workFrame.contentDocument;
      const slider=d && d.querySelector('#hours');
      if(slider) out.push(slider);
    } catch(e) {}
    try {
      const d=resourcesFrame.contentDocument;
      if(d) out.push(...d.querySelectorAll('.mini-hours-slider'));
    } catch(e) {}
    return out;
  }

  function syncFrom(source, includeChange){
    if(syncing) return;
    syncing=true;
    const value=source.value;
    hourSliders().forEach(target=>{
      if(target===source || target.value===value) return;
      target.value=value;
      const w=target.ownerDocument.defaultView;
      target.dispatchEvent(new w.Event('input',{bubbles:true}));
      if(includeChange) target.dispatchEvent(new w.Event('change',{bubbles:true}));
    });
    syncing=false;
  }

  function bind(){
    hourSliders().forEach(slider=>{
      if(slider.dataset.draftHoursSynced) return;
      slider.dataset.draftHoursSynced='1';
      slider.addEventListener('input',()=>syncFrom(slider,false));
      slider.addEventListener('change',()=>syncFrom(slider,true));
    });
  }

  function afterLoad(){
    setTimeout(bind,0);
    setTimeout(bind,250);
    setTimeout(bind,900);
  }

  workFrame.addEventListener('load',afterLoad);
  resourcesFrame.addEventListener('load',afterLoad);
  afterLoad();
})();
'''
    if '</script>' not in s:
        raise SystemExit('Could not find closing script tag')
    s = s.replace('</script>', sync_js + '\n</script>', 1)

p.write_text(s, encoding='utf-8')
