from pathlib import Path

p=Path('draft-story-0915.html')
s=p.read_text(encoding='utf-8')

# Clarify that the displayed monthly equivalent includes the required ResNet fee by default,
# while allowing a room-charge-only comparison view.
old_method='''    <p class="method">Projected 2026–27 residence hall rates from official housing rates, converted from two semester charges to a 9-month academic-year monthly equivalent. The calculation includes the required $150-per-semester ResNet fee, which residents pay for internet access but which goes to OIT, not University Housing. Summer is excluded. Winter break is a separate housing term for most residents and is not included unless selected below. Furnishing, included services, shared-room occupancy and lease lengths differ from off-campus offers.</p>'''
new_method='''    <p class="method">Projected 2026–27 residence hall rates from official housing rates, converted from two semester charges to a 9-month academic-year monthly equivalent. By default, the calculation includes the required $150-per-semester ResNet fee, which residents pay for internet access but which goes to OIT, not University Housing. Use the ResNet toggle below to view the room charge alone; residents still pay the required fee. Summer is excluded. Winter break is a separate housing term for most residents and is not included unless selected below. Furnishing, included services, shared-room occupancy and lease lengths differ from off-campus offers.</p>'''
if old_method in s:
    s=s.replace(old_method,new_method,1)

# Add the ResNet control directly under the existing winter-break control.
if 'id="resnet-fee"' not in s:
    winter_block='''    <div class="break-option">
      <input type="checkbox" id="winter-break">
      <label for="winter-break">
        <strong>Include a full winter-break stay</strong>
        <span class="break-note">Uses NC State’s 2025–26 full-break rate of $360 ($15/night). The 2026–27 winter-break charge and dates have not yet been posted, so this is a reference scenario.</span>
      </label>
    </div>'''
    resnet_block=winter_block+'''

    <div class="break-option resnet-option">
      <input type="checkbox" id="resnet-fee" checked>
      <label for="resnet-fee">
        <strong>Include required ResNet fee (+$150/semester)</strong>
        <span class="break-note">Checked by default because residents pay this separate OIT charge for internet access. Turn it off only to compare University Housing room charges without the internet fee.</span>
      </label>
    </div>'''
    if winter_block not in s:
        raise SystemExit('Could not find winter-break control')
    s=s.replace(winter_block,resnet_block,1)

css_marker='/* ResNet comparison toggle */'
if css_marker not in s:
    css='''

/* ResNet comparison toggle */
.break-option + .break-option{
  margin-top:-12px;
  border-top:0;
}
/* End ResNet comparison toggle */
'''
    s=s.replace('</style>',css+'\n</style>',1)

old_calc='''(function(){
  const box=document.getElementById('winter-break');
  const doubleOut=document.getElementById('double-monthly');
  const singleOut=document.getElementById('single-monthly');
  function money(n){ return Math.round(n).toLocaleString('en-US'); }
  function render(){
    const winter=box.checked ? 360 : 0;
    const doubleYear=(3970+150)*2+winter;
    const singleYear=(4600+150)*2+winter;
    doubleOut.textContent='≈ $'+money(doubleYear/9)+'/month';
    singleOut.textContent='≈ $'+money(singleYear/9)+'/month';
  }
  box.addEventListener('change',render);
  render();
})();'''
new_calc='''(function(){
  const winterBox=document.getElementById('winter-break');
  const resnetBox=document.getElementById('resnet-fee');
  const doubleOut=document.getElementById('double-monthly');
  const singleOut=document.getElementById('single-monthly');
  function money(n){ return Math.round(n).toLocaleString('en-US'); }
  function render(){
    const winter=winterBox && winterBox.checked ? 360 : 0;
    const resnet=resnetBox && resnetBox.checked ? 150 : 0;
    const doubleYear=(3970+resnet)*2+winter;
    const singleYear=(4600+resnet)*2+winter;
    doubleOut.textContent='≈ $'+money(doubleYear/9)+'/month';
    singleOut.textContent='≈ $'+money(singleYear/9)+'/month';
    const suffix=resnet ? 'per student' : 'per student · ResNet excluded';
    if(doubleOut.nextElementSibling) doubleOut.nextElementSibling.textContent=suffix;
    if(singleOut.nextElementSibling) singleOut.nextElementSibling.textContent=suffix;
  }
  if(winterBox) winterBox.addEventListener('change',render);
  if(resnetBox) resnetBox.addEventListener('change',render);
  render();
})();'''
if old_calc in s:
    s=s.replace(old_calc,new_calc,1)
elif "const resnetBox=document.getElementById('resnet-fee');" not in s:
    raise SystemExit('Could not find monthly-equivalent calculation')

# Keep the campus comparison values in the embedded off-campus panel synchronized
# with the top-level ResNet toggle, even though that lower control still exposes only winter break.
old_vars='''        const embeddedBox=breakRow.querySelector('.draft-campus-break-checkbox');
        const parentBox=document.getElementById('winter-break');
        const singleValue=single && single.querySelector('.rent-benchmark-value');
        const sharedValue=shared && shared.querySelector('.rent-benchmark-value');

        function renderEmbeddedWinter(checked){
          if(singleValue) singleValue.innerHTML='≈ $'+(checked ? '1,096' : '1,056')+'/month<span>per student</span>';
          if(sharedValue) sharedValue.innerHTML='≈ $'+(checked ? '956' : '916')+'/month<span>per student</span>';
          if(embeddedBox) embeddedBox.checked=!!checked;
        }'''
new_vars='''        const embeddedBox=breakRow.querySelector('.draft-campus-break-checkbox');
        const parentBox=document.getElementById('winter-break');
        const parentResnetBox=document.getElementById('resnet-fee');
        const singleValue=single && single.querySelector('.rent-benchmark-value');
        const sharedValue=shared && shared.querySelector('.rent-benchmark-value');

        function renderEmbeddedCampus(winterChecked,resnetChecked){
          const winter=winterChecked ? 360 : 0;
          const resnet=resnetChecked ? 150 : 0;
          const singleMonthly=Math.round(((4600+resnet)*2+winter)/9).toLocaleString('en-US');
          const sharedMonthly=Math.round(((3970+resnet)*2+winter)/9).toLocaleString('en-US');
          const suffix=resnetChecked ? 'per student' : 'per student · ResNet excluded';
          if(singleValue) singleValue.innerHTML='≈ $'+singleMonthly+'/month<span>'+suffix+'</span>';
          if(sharedValue) sharedValue.innerHTML='≈ $'+sharedMonthly+'/month<span>'+suffix+'</span>';
          if(embeddedBox) embeddedBox.checked=!!winterChecked;
        }'''
if old_vars in s:
    s=s.replace(old_vars,new_vars,1)

old_events='''        if(embeddedBox && !embeddedBox.dataset.bound){
          embeddedBox.dataset.bound='1';
          embeddedBox.addEventListener('change',()=>{
            renderEmbeddedWinter(embeddedBox.checked);
            if(parentBox && parentBox.checked!==embeddedBox.checked){
              parentBox.checked=embeddedBox.checked;
              parentBox.dispatchEvent(new Event('change'));
            }
            setTimeout(resize,0);
          });
        }

        if(parentBox){
          renderEmbeddedWinter(parentBox.checked);
          if(!parentBox.dataset.offCampusLinked){
            parentBox.dataset.offCampusLinked='1';
            parentBox.addEventListener('change',()=>{
              renderEmbeddedWinter(parentBox.checked);
              setTimeout(resize,0);
            });
          }
        }'''
new_events='''        if(embeddedBox && !embeddedBox.dataset.bound){
          embeddedBox.dataset.bound='1';
          embeddedBox.addEventListener('change',()=>{
            renderEmbeddedCampus(embeddedBox.checked,parentResnetBox ? parentResnetBox.checked : true);
            if(parentBox && parentBox.checked!==embeddedBox.checked){
              parentBox.checked=embeddedBox.checked;
              parentBox.dispatchEvent(new Event('change'));
            }
            setTimeout(resize,0);
          });
        }

        if(parentBox){
          renderEmbeddedCampus(parentBox.checked,parentResnetBox ? parentResnetBox.checked : true);
          if(!parentBox.dataset.offCampusLinked){
            parentBox.dataset.offCampusLinked='1';
            parentBox.addEventListener('change',()=>{
              renderEmbeddedCampus(parentBox.checked,parentResnetBox ? parentResnetBox.checked : true);
              setTimeout(resize,0);
            });
          }
        }
        if(parentResnetBox && !parentResnetBox.dataset.offCampusLinked){
          parentResnetBox.dataset.offCampusLinked='1';
          parentResnetBox.addEventListener('change',()=>{
            renderEmbeddedCampus(parentBox ? parentBox.checked : false,parentResnetBox.checked);
            setTimeout(resize,0);
          });
        }'''
if old_events in s:
    s=s.replace(old_events,new_events,1)

p.write_text(s,encoding='utf-8')
