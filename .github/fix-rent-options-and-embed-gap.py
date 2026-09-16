from pathlib import Path

# Add explicit off-campus/on-campus choices to the affordability comparison.
p = Path('index.html')
s = p.read_text(encoding='utf-8')

old_options = '<option value="main">Main Campus</option><option value="centennial">Centennial Campus</option><option value="vet">Biomedical Campus</option>'
new_options = '<option value="main">Off campus — Main Campus room mean</option><option value="centennial">Off campus — Centennial Campus room mean</option><option value="vet">Off campus — Biomedical Campus room mean</option><option value="housing-double">On campus — double (shared room; room charge only)</option><option value="housing-single">On campus — single (room charge only)</option>'
if old_options in s:
    s = s.replace(old_options, new_options)
elif 'value="housing-double"' not in s:
    raise SystemExit('Could not find affordability select options')

s = s.replace('<label class="card-rent-area">Rent area', '<label class="card-rent-area">Housing option')
s = s.replace('aria-label="Rent area for the $7.25 monthly-resources comparison"', 'aria-label="Housing option for the $7.25 monthly-resources comparison"')
s = s.replace('aria-label="Rent area for the adjustable-pay monthly-resources comparison"', 'aria-label="Housing option for the adjustable-pay monthly-resources comparison"')

# Give the longer, explicit labels enough room.
s = s.replace(
    '.card-rent-area select{width:132px;max-width:calc(100% - 58px);',
    '.card-rent-area select{width:270px;max-width:calc(100% - 78px);',
)
s = s.replace(
    '.card-rent-area select{width:min(100%,132px)}',
    '.card-rent-area select{width:min(100%,270px)}',
)

old_stats = """  const affordabilityStats=overallDistanceBandSummary(affordabilityCampusKey).perOverall;
  const affordabilityLabel=affordabilityCampusKey==='vet' ? 'Biomedical Campus' : campuses[affordabilityCampusKey].label;"""
new_stats = """  const onCampusAffordability={
    'housing-double':{
      label:'On-campus residence hall double (shared room)',
      stats:{avg_low:(3970*2/9),avg_high:(3970*2/9),midpoint:(3970*2/9)}
    },
    'housing-single':{
      label:'On-campus residence hall single',
      stats:{avg_low:(4600*2/9),avg_high:(4600*2/9),midpoint:(4600*2/9)}
    }
  };
  const onCampusSelection=onCampusAffordability[affordabilityCampusKey] || null;
  const affordabilityStats=onCampusSelection ? onCampusSelection.stats : overallDistanceBandSummary(affordabilityCampusKey).perOverall;
  const affordabilityLabel=onCampusSelection ? onCampusSelection.label : (affordabilityCampusKey==='vet' ? 'Biomedical Campus' : campuses[affordabilityCampusKey].label);"""
if old_stats in s:
    s = s.replace(old_stats, new_stats, 1)
elif 'const onCampusAffordability={' not in s:
    raise SystemExit('Could not find affordability stats block')

old_title = """  const rentTitle=`${affordabilityLabel} room rent`;
  document.getElementById('burdenRentTitleLow').textContent=rentTitle;
  document.getElementById('burdenRentTitleHigh').textContent=rentTitle;
  const meanStats={...affordabilityStats,label:'mean'};"""
new_title = """  const rentTitle=onCampusSelection ? `${affordabilityLabel} room charge` : `Off-campus ${affordabilityLabel} room rent`;
  document.getElementById('burdenRentTitleLow').textContent=rentTitle;
  document.getElementById('burdenRentTitleHigh').textContent=rentTitle;
  const meanStats={...affordabilityStats,label:onCampusSelection ? 'monthly equivalent' : 'mean'};"""
if old_title in s:
    s = s.replace(old_title, new_title, 1)
elif "label:onCampusSelection ? 'monthly equivalent' : 'mean'" not in s:
    raise SystemExit('Could not find affordability title block')

old_handler = """document.querySelectorAll('.affordability-campus-select').forEach(select=>select.addEventListener('change',event=>{
  setCampus(event.target.value);
}));"""
new_handler = """document.querySelectorAll('.affordability-campus-select').forEach(select=>select.addEventListener('change',event=>{
  const key=event.target.value;
  if(key==='housing-double' || key==='housing-single'){
    affordabilityCampusKey=key;
    document.querySelectorAll('.affordability-campus-select').forEach(other=>other.value=key);
    updateAffordability();
  }else{
    setCampus(key);
  }
}));"""
if old_handler in s:
    s = s.replace(old_handler, new_handler, 1)
elif "key==='housing-double' || key==='housing-single'" not in s:
    raise SystemExit('Could not find affordability select handler')

p.write_text(s, encoding='utf-8')

# Remove the extra blank area below the embedded off-campus comparison by sizing
# the iframe to the visible wrapper instead of the document scroll height.
p = Path('draft-story-0915.html')
s = p.read_text(encoding='utf-8')
old_resize = "frame.style.height=Math.ceil(Math.max(d.body.scrollHeight,d.documentElement.scrollHeight)+4)+'px';"
new_resize = "frame.style.height=Math.ceil(wrapper.getBoundingClientRect().height+4)+'px';"
if old_resize in s:
    s = s.replace(old_resize, new_resize, 1)
elif new_resize not in s:
    raise SystemExit('Could not find off-campus iframe resize rule')
p.write_text(s, encoding='utf-8')

# Keep the standalone/original index comparison in sync with the updated story:
# show room charge alone by default, then let readers add winter break and ResNet.
p = Path('index.html')
s = p.read_text(encoding='utf-8')

old_note = '''<div class="housing-monthly-note">Projected 2026–27 residence hall rates from <a href="https://housing.dasa.ncsu.edu/residential-communities/costs/" target="_blank" rel="noopener noreferrer">official housing rates</a>, converted from two semester charges to a 9-month academic-year monthly equivalent. Includes required ResNet; summer is excluded. Furnishing, included services, shared-room occupancy and lease lengths differ from off-campus offers.</div>'''
new_note = '''<div class="housing-monthly-note">Projected 2026–27 residence hall rates from <a href="https://housing.dasa.ncsu.edu/residential-communities/costs/" target="_blank" rel="noopener noreferrer">official housing rates</a>, converted from two semester charges to a 9-month academic-year monthly equivalent. By default, the comparison shows the University Housing room charge alone. Residents also pay a required $150-per-semester ResNet fee for internet access, which goes to OIT rather than University Housing; use the ResNet checkbox below to add it. Summer is excluded. Winter break is a separate housing term for most residents and is not included unless selected below. Furnishing, included services, shared-room occupancy and lease lengths differ from off-campus offers.</div>'''
if old_note in s:
    s = s.replace(old_note, new_note, 1)
elif 'By default, the comparison shows the University Housing room charge alone.' not in s:
    raise SystemExit('Could not update main residence-hall method note')

s = s.replace(
    '<div class="rent-benchmark-note">$3,970/semester + $150 required ResNet fee</div>',
    '<div class="rent-benchmark-note">$3,970/semester housing · Required ResNet: +$150/semester (paid to OIT)</div>',
    1,
)
s = s.replace(
    '<div class="rent-benchmark-note">$4,600/semester + $150 required ResNet fee</div>',
    '<div class="rent-benchmark-note">$4,600/semester housing · Required ResNet: +$150/semester (paid to OIT)</div>',
    1,
)

if 'id="main-double-monthly"' not in s:
    old_double = '<div class="rent-benchmark-value">≈ $916/month<span>per student</span></div>'
    new_double = '<div class="rent-benchmark-value" id="main-double-monthly">≈ $882/month<span>per student · ResNet excluded</span></div>'
    if old_double not in s:
        raise SystemExit('Could not find main double monthly value')
    s = s.replace(old_double, new_double, 1)

if 'id="main-single-monthly"' not in s:
    old_single = '<div class="rent-benchmark-value">≈ $1,056/month<span>per student</span></div>'
    new_single = '<div class="rent-benchmark-value" id="main-single-monthly">≈ $1,022/month<span>per student · ResNet excluded</span></div>'
    if old_single not in s:
        raise SystemExit('Could not find main single monthly value')
    s = s.replace(old_single, new_single, 1)

if 'class="main-campus-comparison-options"' not in s:
    anchor = '''

        </div>

        <div class="housing-monthly housing-budget-section">'''
    controls = '''

          <div class="main-campus-comparison-options">
            <div class="main-campus-option">
              <input type="checkbox" id="main-winter-break">
              <label for="main-winter-break"><strong>Full winter break (+$360)</strong><span>2025–26 reference rate; 2026–27 rate not yet posted.</span></label>
            </div>
            <div class="main-campus-option">
              <input type="checkbox" id="main-resnet-fee">
              <label for="main-resnet-fee"><strong>Required ResNet (+$150/semester; ≈ +$33/month)</strong><span>Paid to OIT for internet access.</span></label>
            </div>
          </div>

        </div>

        <div class="housing-monthly housing-budget-section">'''
    if anchor not in s:
        raise SystemExit('Could not find main housing budget transition')
    s = s.replace(anchor, controls, 1)

css_marker = '/* Main residence hall comparison controls */'
if css_marker not in s:
    css = '''

/* Main residence hall comparison controls */
.main-campus-comparison-options{
  display:grid;
  grid-template-columns:19fr 20fr;
  gap:12px;
  margin-top:10px;
}
.main-campus-option{
  display:flex;
  align-items:flex-start;
  gap:9px;
  min-width:0;
  padding:10px 12px;
  border:1px solid var(--line);
  background:var(--soft2);
  font-size:9px;
  line-height:1.35;
}
.main-campus-option input{
  flex:0 0 auto;
  margin:2px 0 0;
}
.main-campus-option label{
  min-width:0;
  cursor:pointer;
}
.main-campus-option strong{
  display:inline;
  font-size:10px;
}
.main-campus-option span{
  margin-left:6px;
  color:var(--muted);
}
@media (max-width:720px){
  .main-campus-comparison-options{grid-template-columns:1fr;gap:7px;}
  .main-campus-option span{display:block;margin:2px 0 0;}
}
/* End main residence hall comparison controls */
'''
    s = s.replace('</style>', css + '\n</style>', 1)

js_marker = 'function renderMainCampusRates()'
if js_marker not in s:
    js = '''
<script>
(function(){
  const winterBox=document.getElementById('main-winter-break');
  const resnetBox=document.getElementById('main-resnet-fee');
  const doubleOut=document.getElementById('main-double-monthly');
  const singleOut=document.getElementById('main-single-monthly');
  if(!doubleOut || !singleOut) return;

  function money(n){ return Math.round(n).toLocaleString('en-US'); }
  function renderMainCampusRates(){
    const winter=winterBox && winterBox.checked ? 360 : 0;
    const resnet=resnetBox && resnetBox.checked ? 150 : 0;
    const doubleMonthly=((3970+resnet)*2+winter)/9;
    const singleMonthly=((4600+resnet)*2+winter)/9;
    const suffix=resnet ? 'per student' : 'per student · ResNet excluded';
    doubleOut.innerHTML='≈ $'+money(doubleMonthly)+'/month<span>'+suffix+'</span>';
    singleOut.innerHTML='≈ $'+money(singleMonthly)+'/month<span>'+suffix+'</span>';
  }

  if(winterBox) winterBox.addEventListener('change',renderMainCampusRates);
  if(resnetBox) resnetBox.addEventListener('change',renderMainCampusRates);
  renderMainCampusRates();
})();
</script>
'''
    if '</body>' not in s:
        raise SystemExit('Could not find body close for main housing controls')
    s = s.replace('</body>', js + '\n</body>', 1)

p.write_text(s, encoding='utf-8')
