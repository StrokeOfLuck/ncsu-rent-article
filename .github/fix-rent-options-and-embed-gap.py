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
