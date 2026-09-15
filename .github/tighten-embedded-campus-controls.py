from pathlib import Path

p = Path('draft-story-0915.html')
s = p.read_text(encoding='utf-8')

# The embedded campus comparison changes both for winter-break housing and for the
# separately billed required ResNet fee. Put both controls in the same row above
# the campus comparison.
old_html = '''          breakRow.innerHTML='<div class="draft-campus-break-control"><label><input type="checkbox" class="draft-campus-break-checkbox"> <strong>Add full winter break (+$360)</strong></label><span class="draft-campus-break-year">2025–26 rate</span><span class="draft-campus-break-info" tabindex="0" role="img" aria-label="Uses NC State’s 2025–26 full-break rate of $360 at $15 per night. The 2026–27 winter-break charge and dates have not yet been posted, so this is a reference scenario." title="Uses NC State’s 2025–26 full-break rate of $360 ($15/night). The 2026–27 winter-break charge and dates have not yet been posted, so this is a reference scenario.">ⓘ</span></div>';'''
new_html = '''          breakRow.innerHTML='<div class="draft-campus-break-control"><label><input type="checkbox" class="draft-campus-break-checkbox"> <strong>Add full winter break (+$360)</strong></label><span class="draft-campus-break-year">2025–26 rate</span><span class="draft-campus-break-info" tabindex="0" role="img" aria-label="Uses NC State’s 2025–26 full-break rate of $360 at $15 per night. The 2026–27 winter-break charge and dates have not yet been posted, so this is a reference scenario." title="Uses NC State’s 2025–26 full-break rate of $360 ($15/night). The 2026–27 winter-break charge and dates have not yet been posted, so this is a reference scenario.">ⓘ</span><span class="draft-campus-option-divider" aria-hidden="true"></span><label><input type="checkbox" class="draft-campus-resnet-checkbox"> <strong>Add required ResNet (+$150/semester; ≈ +$33/month)</strong></label><span class="draft-campus-resnet-note">Paid to OIT</span></div>';'''
if old_html in s:
    s = s.replace(old_html, new_html, 1)
elif 'draft-campus-resnet-checkbox' not in s:
    raise SystemExit('Could not find embedded winter-break control')

old_vars = '''        const embeddedBox=breakRow.querySelector('.draft-campus-break-checkbox');
        const parentBox=document.getElementById('winter-break');
        const parentResnetBox=document.getElementById('resnet-fee');'''
new_vars = '''        const embeddedBox=breakRow.querySelector('.draft-campus-break-checkbox');
        const embeddedResnetBox=breakRow.querySelector('.draft-campus-resnet-checkbox');
        const parentBox=document.getElementById('winter-break');
        const parentResnetBox=document.getElementById('resnet-fee');'''
if old_vars in s:
    s = s.replace(old_vars, new_vars, 1)

# Keep the embedded ResNet control synchronized with the parent calculation.
needle = '''          if(embeddedBox) embeddedBox.checked=!!winterChecked;'''
if needle in s and 'if(embeddedResnetBox) embeddedResnetBox.checked=!!resnetChecked;' not in s[s.find(needle):s.find(needle)+250]:
    s = s.replace(
        needle,
        needle + '''\n          if(embeddedResnetBox) embeddedResnetBox.checked=!!resnetChecked;''',
        1,
    )

if 'embeddedResnetBox.dataset.bound' not in s:
    marker = '''
        if(parentBox){'''
    binding = '''
        if(embeddedResnetBox && !embeddedResnetBox.dataset.bound){
          embeddedResnetBox.dataset.bound='1';
          embeddedResnetBox.addEventListener('change',()=>{
            renderEmbeddedCampus(parentBox ? parentBox.checked : false,embeddedResnetBox.checked);
            if(parentResnetBox && parentResnetBox.checked!==embeddedResnetBox.checked){
              parentResnetBox.checked=embeddedResnetBox.checked;
              parentResnetBox.dispatchEvent(new Event('change'));
            }
            setTimeout(resize,0);
          });
        }

        if(parentBox){'''
    if marker not in s:
        raise SystemExit('Could not find embedded campus binding insertion point')
    s = s.replace(marker, binding, 1)

# Remove the intentionally empty left grid column from the option row.
s = s.replace(
    '''            .draft-campus-break-row{
              display:grid;
              grid-template-columns:repeat(3,minmax(0,1fr));
              background:#fff;
              border-bottom:1px solid var(--line);
            }''',
    '''            .draft-campus-break-row{
              display:grid;
              grid-template-columns:1fr;
              background:#fff;
              border-bottom:1px solid var(--line);
            }''',
    1,
)
s = s.replace(
    '''            .draft-campus-break-control{
              grid-column:2 / 4;''',
    '''            .draft-campus-break-control{
              grid-column:1 / -1;''',
    1,
)
s = s.replace(
    '''              border-left:1px solid var(--line);
              color:#514d47;''',
    '''              border-left:0;
              color:#514d47;''',
    1,
)

if '.draft-campus-option-divider{' not in s:
    marker = '''            .draft-campus-break-control label{'''
    styles = '''            .draft-campus-option-divider{
              width:1px;
              align-self:stretch;
              min-height:22px;
              margin:0 4px;
              background:var(--line);
            }
            .draft-campus-resnet-note{
              color:#746f68;
              white-space:nowrap;
            }
            .draft-campus-break-control label{'''
    if marker not in s:
        raise SystemExit('Could not find campus control label styles')
    s = s.replace(marker, styles, 1)

# Make the control row read as the attached header for the rate cards, rather than
# a separate floating band. Remove the gap and let the row/strip share one border.
s = s.replace(
    '''            .draft-comparison-strip{
              display:grid;
              grid-template-columns:repeat(3,minmax(0,1fr));
              margin-top:8px;
              border-top:1px solid var(--line);''',
    '''            .draft-comparison-strip{
              display:grid;
              grid-template-columns:repeat(3,minmax(0,1fr));
              margin-top:0;
              border-top:0;''',
    1,
)
s = s.replace(
    '''            .draft-campus-break-row{
              display:grid;
              grid-template-columns:1fr;
              background:#fff;
              border-bottom:1px solid var(--line);
            }''',
    '''            .draft-campus-break-row{
              display:grid;
              grid-template-columns:1fr;
              margin:8px 0 0;
              background:#fff;
              border-top:1px solid var(--line);
              border-bottom:1px solid var(--line);
            }''',
    1,
)
s = s.replace(
    '''              padding:9px 16px 10px;''',
    '''              padding:8px 16px 9px;''',
    1,
)

# On narrow screens let the two options wrap cleanly and hide the divider.
if '.draft-campus-option-divider{display:none;}' not in s:
    marker = '''              .draft-campus-break-control{
                grid-column:1;
                border-left:0;
                flex-wrap:wrap;
              }'''
    replacement = '''              .draft-campus-break-control{
                grid-column:1;
                border-left:0;
                flex-wrap:wrap;
              }
              .draft-campus-option-divider{display:none;}'''
    if marker in s:
        s = s.replace(marker, replacement, 1)

p.write_text(s, encoding='utf-8')
