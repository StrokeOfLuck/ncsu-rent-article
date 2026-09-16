from pathlib import Path
import re

p = Path('draft-story-0915.html')
s = p.read_text(encoding='utf-8')

# ResNet is a required charge, so it should be included in the displayed monthly
# equivalent rather than presented as an optional checkbox.
method_variants = [
    '''Projected 2026–27 residence hall rates from official housing rates, converted from two semester charges to a 9-month academic-year monthly equivalent. By default, the comparison shows the University Housing room charge alone. Residents also pay a required $150-per-semester ResNet fee for internet access, which goes to OIT rather than University Housing; use the ResNet checkbox below to add it.''',
    '''Projected 2026–27 residence hall rates from official housing rates, converted from two semester charges to a 9-month academic-year monthly equivalent. The calculation includes the required $150-per-semester ResNet fee for internet access, which residents must pay but which goes to OIT rather than University Housing. The ResNet checkbox is checked by default; turn it off only to view the University Housing room charge by itself.''',
]
final_method = '''Projected 2026–27 residence hall rates from official housing rates, converted from two semester charges to a 9-month academic-year monthly equivalent. The calculation includes the required $150-per-semester ResNet fee for internet access. ResNet is paid to OIT for internet access, not to University Housing. Summer is excluded. Winter break is a separate housing term for most residents and is not included unless selected below. Furnishing, included services, shared-room occupancy and lease lengths differ from off-campus offers.'''
for old in method_variants:
    if old in s:
        # Include the trailing common sentences in the replacement only once.
        tail = ''' Summer is excluded. Winter break is a separate housing term for most residents and is not included unless selected below. Furnishing, included services, shared-room occupancy and lease lengths differ from off-campus offers.'''
        if old + tail in s:
            s = s.replace(old + tail, final_method, 1)
        else:
            s = s.replace(old, final_method.split(' Summer is excluded.')[0], 1)
        break

s = s.replace('≈ $882/month', '≈ $916/month', 1)
s = s.replace('≈ $1,022/month', '≈ $1,056/month', 1)

s = s.replace(
    '$3,970/semester housing · Required ResNet: +$150/semester (paid to OIT)',
    '$3,970/semester housing (+$150/semester required ResNet fee; paid to OIT for internet, not University Housing)',
)
s = s.replace(
    '$4,600/semester housing · Required ResNet: +$150/semester (paid to OIT)',
    '$4,600/semester housing (+$150/semester required ResNet fee; paid to OIT for internet, not University Housing)',
)

# Remove the parent-page ResNet option entirely; winter break remains optional.
s = re.sub(
    r'\n\s*<div class="break-option resnet-option">\s*<input type="checkbox" id="resnet-fee"(?: checked)?>\s*<label for="resnet-fee">.*?</label>\s*</div>',
    '',
    s,
    count=1,
    flags=re.S,
)
s = s.replace('grid-template-columns:1fr 1fr;', 'grid-template-columns:1fr;', 1)

# The required fee is always part of the parent calculation.
s = s.replace("    const resnet=resnetBox && resnetBox.checked ? 150 : 0;", "    const resnet=150;", 1)
s = s.replace("    const suffix=resnet ? 'per student' : 'per student · ResNet excluded';", "    const suffix='per student';", 1)

# Keep the embedded comparison consistent: no ResNet checkbox, and always include it.
s = re.sub(
    r"breakRow\.innerHTML='<div class=\"draft-campus-break-control\">.*?</div>';",
    "breakRow.innerHTML='<div class=\"draft-campus-break-control\"><label><input type=\"checkbox\" class=\"draft-campus-break-checkbox\"> <strong>Add full winter break (+$360)</strong></label><span class=\"draft-campus-break-year\">2025–26 rate</span><span class=\"draft-campus-break-info\" tabindex=\"0\" role=\"img\" aria-label=\"Uses NC State’s 2025–26 full-break rate of $360 at $15 per night. The 2026–27 winter-break charge and dates have not yet been posted, so this is a reference scenario.\" title=\"Uses NC State’s 2025–26 full-break rate of $360 ($15/night). The 2026–27 winter-break charge and dates have not yet been posted, so this is a reference scenario.\">ⓘ</span></div>';",
    s,
    count=1,
    flags=re.S,
)
s = s.replace("          const resnet=resnetChecked ? 150 : 0;", "          const resnet=150;", 1)
s = s.replace("          const suffix=resnetChecked ? 'per student' : 'per student · ResNet excluded';", "          const suffix='per student';", 1)

# Put the required fee back in parentheses on the embedded residence-hall cards.
s = s.replace(
    "'$4,600/semester housing · Required ResNet: +$150/semester (paid to OIT)'",
    "'$4,600/semester housing (+$150/semester required ResNet fee; paid to OIT for internet, not University Housing)'",
)
s = s.replace(
    "'$3,970/semester housing · Required ResNet: +$150/semester (paid to OIT)'",
    "'$3,970/semester housing (+$150/semester required ResNet fee; paid to OIT for internet, not University Housing)'",
)
s = s.replace(
    "'$150 required ResNet fee (paid to OIT)'",
    "'$150 required ResNet fee (paid to OIT for internet, not University Housing)'",
)

p.write_text(s, encoding='utf-8')
