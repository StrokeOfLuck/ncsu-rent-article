from pathlib import Path
import re

p = Path('draft-story-0915.html')
s = p.read_text(encoding='utf-8')

# Keep residence-hall and budget cards side-by-side on desktop.
s = re.sub(
    r'(\.rate-grid,\s*\n\s*\.budget-grid \{\s*\n\s*display:grid;\s*\n\s*grid-template-columns:)1fr(;)',
    r'\g<1>1fr 1fr\2',
    s,
    count=1,
)

# Only winter break remains an optional comparison control.
s = re.sub(
    r'(\.comparison-options\{\s*\n\s*display:grid;\s*\n\s*grid-template-columns:)1fr 1fr(;)',
    r'\g<1>1fr\2',
    s,
    count=1,
)

# Final explanatory copy: ResNet is required and included, but billed by OIT.
method_re = re.compile(r'(<p class="method">)Projected 2026–27 residence hall rates.*?(</p>)', re.S)
method = (
    'Projected 2026–27 residence hall rates from official housing rates, converted from two semester charges '
    'to a 9-month academic-year monthly equivalent. The calculation includes the required $150-per-semester '
    'ResNet fee. ResNet is paid to OIT for internet access, not to University Housing. Summer is excluded. '
    'Winter break is a separate housing term for most residents and is not included unless selected below. '
    'Furnishing, included services, shared-room occupancy and lease lengths differ from off-campus offers.'
)
s = method_re.sub(r'\1' + method + r'\2', s, count=1)

s = s.replace('≈ $882/month', '≈ $916/month', 1)
s = s.replace('≈ $1,022/month', '≈ $1,056/month', 1)

# Put the required OIT fee in parentheses beside the semester housing charge.
s = re.sub(
    r'\$3,970/semester housing(?: · Required ResNet: \+\$150/semester \(paid to OIT\)| \(\+\$150/semester required ResNet fee; paid to OIT for internet, not University Housing\))',
    '$3,970/semester housing (+$150/semester required ResNet fee; paid to OIT for internet, not University Housing)',
    s,
)
s = re.sub(
    r'\$4,600/semester housing(?: · Required ResNet: \+\$150/semester \(paid to OIT\)| \(\+\$150/semester required ResNet fee; paid to OIT for internet, not University Housing\))',
    '$4,600/semester housing (+$150/semester required ResNet fee; paid to OIT for internet, not University Housing)',
    s,
)

# Remove any remaining parent ResNet checkbox block.
s = re.sub(
    r'\n\s*<div class="break-option resnet-option">.*?</div>',
    '',
    s,
    count=1,
    flags=re.S,
)

# Required fee is always included in the top calculation.
s = s.replace("    const resnet=resnetBox && resnetBox.checked ? 150 : 0;", "    const resnet=150;", 1)
s = s.replace("    const suffix=resnet ? 'per student' : 'per student · ResNet excluded';", "    const suffix='per student';", 1)

# Remove the embedded ResNet checkbox from the generated control row.
s = re.sub(
    r"^\s*breakRow\.innerHTML='[^\n]*class=\\\"draft-campus-resnet-checkbox\\\"[^\n]*';\s*$",
    "          breakRow.innerHTML='<div class=\"draft-campus-break-control\"><label><input type=\"checkbox\" class=\"draft-campus-break-checkbox\"> <strong>Add full winter break (+$360)</strong></label><span class=\"draft-campus-break-year\">2025–26 rate</span><span class=\"draft-campus-break-info\" tabindex=\"0\" role=\"img\" aria-label=\"Uses NC State’s 2025–26 full-break rate of $360 at $15 per night. The 2026–27 winter-break charge and dates have not yet been posted, so this is a reference scenario.\" title=\"Uses NC State’s 2025–26 full-break rate of $360 ($15/night). The 2026–27 winter-break charge and dates have not yet been posted, so this is a reference scenario.\">ⓘ</span></div>';",
    s,
    count=1,
    flags=re.M,
)

# Embedded residence-hall figures also always include ResNet.
s = s.replace("          const resnet=resnetChecked ? 150 : 0;", "          const resnet=150;", 1)
s = s.replace("          const suffix=resnetChecked ? 'per student' : 'per student · ResNet excluded';", "          const suffix='per student';", 1)

# Normalize any embedded card note transformations to the parenthetical wording.
s = s.replace(
    "$4,600/semester housing · Required ResNet: +$150/semester (paid to OIT)",
    "$4,600/semester housing (+$150/semester required ResNet fee; paid to OIT for internet, not University Housing)",
)
s = s.replace(
    "$3,970/semester housing · Required ResNet: +$150/semester (paid to OIT)",
    "$3,970/semester housing (+$150/semester required ResNet fee; paid to OIT for internet, not University Housing)",
)
s = s.replace(
    "$150 required ResNet fee (paid to OIT)",
    "$150 required ResNet fee (paid to OIT for internet, not University Housing)",
)

# Guardrails: no actual ResNet checkbox markup may remain. Old null-safe JS selectors
# can remain without rendering a control, but the UI itself must not offer a choice.
if 'id="resnet-fee"' in s:
    raise SystemExit('Parent ResNet checkbox still present')
if 'class=\"draft-campus-resnet-checkbox\"' in s:
    raise SystemExit('Embedded ResNet checkbox markup still present')
if '.rate-grid,\n  .budget-grid {\n    display:grid;\n    grid-template-columns:1fr 1fr;' not in s:
    raise SystemExit('Desktop rate grid was not restored')

p.write_text(s, encoding='utf-8')
