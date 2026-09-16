from pathlib import Path
import re

# -----------------------------------------------------------------------------
# Story draft: ResNet is required and always included in the on-campus figures.
# -----------------------------------------------------------------------------
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

# Link the compact advertised-rent card directly to the room-only Excel audit
# reference as well as the methodology explanation.
old_embed_note = '''          note.innerHTML='<strong>Advertised rent only.</strong> Utilities and fees vary by listing; some are included and some are excluded as extra charges. <a href="references.html#rental-method">How this is calculated</a>';'''
new_embed_note = '''          note.innerHTML='<strong>Advertised rent only.</strong> Utilities and fees vary by listing; some are included and some are excluded as extra charges. <a href="references.html#rental-method">How this is calculated</a> · <a href="references.html#room-rent-audit">Room-listing Excel audit</a>';'''
if old_embed_note in s:
    s = s.replace(old_embed_note, new_embed_note, 1)
elif 'Room-listing Excel audit' not in s:
    raise SystemExit('Could not add room Excel audit link to embedded comparison')

# Guardrails: no actual ResNet checkbox markup may remain. Old null-safe JS selectors
# can remain without rendering a control, but the UI itself must not offer a choice.
if 'id="resnet-fee"' in s:
    raise SystemExit('Parent ResNet checkbox still present')
if 'class=\"draft-campus-resnet-checkbox\"' in s:
    raise SystemExit('Embedded ResNet checkbox markup still present')
if '.rate-grid,\n  .budget-grid {\n    display:grid;\n    grid-template-columns:1fr 1fr;' not in s:
    raise SystemExit('Desktop rate grid was not restored')

p.write_text(s, encoding='utf-8')

# -----------------------------------------------------------------------------
# Main interactive page: use the same ResNet-inclusive figures everywhere.
# -----------------------------------------------------------------------------
p = Path('index.html')
s = p.read_text(encoding='utf-8')

# The dropdown should no longer imply that readers can choose a room-charge-only
# version. ResNet is required, so say it is included.
s = s.replace(
    'On campus — double (shared room; room charge only)',
    'On campus — double (shared room; required ResNet included)',
)
s = s.replace(
    'On campus — single (room charge only)',
    'On campus — single (required ResNet included)',
)

# Recalculate the on-campus affordability options with the required $150 fee in
# each semester. This updates the displayed monthly equivalent and every burden /
# resources percentage derived from the selected housing cost.
s = s.replace(
    "stats:{avg_low:(3970*2/9),avg_high:(3970*2/9),midpoint:(3970*2/9)}",
    "stats:{avg_low:((3970+150)*2/9),avg_high:((3970+150)*2/9),midpoint:((3970+150)*2/9)}",
)
s = s.replace(
    "stats:{avg_low:(4600*2/9),avg_high:(4600*2/9),midpoint:(4600*2/9)}",
    "stats:{avg_low:((4600+150)*2/9),avg_high:((4600+150)*2/9),midpoint:((4600+150)*2/9)}",
)

# The card title should describe the housing option, not call it a room charge,
# since the displayed amount also contains the required OIT ResNet fee.
s = s.replace(
    "const rentTitle=onCampusSelection ? `${affordabilityLabel} room charge` : `Off-campus ${affordabilityLabel} room rent`;",
    "const rentTitle=onCampusSelection ? affordabilityLabel : `Off-campus ${affordabilityLabel} room rent`;",
)

# Add the billing clarification directly under the dropdown whenever an on-campus
# option is selected. Keep the existing wage note for off-campus selections.
old_sub_anchor = """  document.getElementById('burdenRentTitleLow').textContent=rentTitle;
  document.getElementById('burdenRentTitleHigh').textContent=rentTitle;
  const meanStats={...affordabilityStats,label:onCampusSelection ? 'monthly equivalent' : 'mean'};"""
new_sub_anchor = """  document.getElementById('burdenRentTitleLow').textContent=rentTitle;
  document.getElementById('burdenRentTitleHigh').textContent=rentTitle;
  const burdenSub=onCampusSelection
    ? 'Gross pay per month. On-campus figure includes the required $150/semester ResNet fee, paid to OIT for internet, not University Housing.'
    : 'Gross pay per month. Work pay assumes 52 paid weeks/year.';
  document.getElementById('burdenSubLow').textContent=burdenSub;
  document.getElementById('burdenSubHigh').textContent=burdenSub;
  const meanStats={...affordabilityStats,label:onCampusSelection ? 'monthly equivalent' : 'mean'};"""
if old_sub_anchor in s:
    s = s.replace(old_sub_anchor, new_sub_anchor, 1)
elif "On-campus figure includes the required $150/semester ResNet fee" not in s:
    raise SystemExit('Could not add affordability ResNet billing note')

# The residence-hall comparison itself must also include ResNet by default. It is
# required, so only winter break remains an optional checkbox.
main_note_re = re.compile(r'(<div class="housing-monthly-note">)Projected 2026–27 residence hall rates.*?(</div>)', re.S)
main_note = (
    'Projected 2026–27 residence hall rates from <a href="https://housing.dasa.ncsu.edu/residential-communities/costs/" target="_blank" rel="noopener noreferrer">official housing rates</a>, '
    'converted from two semester charges to a 9-month academic-year monthly equivalent. The calculation includes '
    'the required $150-per-semester ResNet fee, which is paid to OIT for internet access rather than University Housing. '
    'Summer is excluded. Winter break is a separate housing term for most residents and is not included unless selected below. '
    'Furnishing, included services, shared-room occupancy and lease lengths differ from off-campus offers.'
)
s, main_note_count = main_note_re.subn(r'\1' + main_note + r'\2', s, count=1)
if main_note_count != 1:
    raise SystemExit('Could not update main residence-hall method note')

# Make the static figures match the required-fee calculation before JS runs.
s = re.sub(
    r'<div class="rent-benchmark-value" id="main-double-monthly">.*?</div>',
    '<div class="rent-benchmark-value" id="main-double-monthly">≈ $916/month<span>per student</span></div>',
    s,
    count=1,
    flags=re.S,
)
s = re.sub(
    r'<div class="rent-benchmark-value" id="main-single-monthly">.*?</div>',
    '<div class="rent-benchmark-value" id="main-single-monthly">≈ $1,056/month<span>per student</span></div>',
    s,
    count=1,
    flags=re.S,
)

# Remove the ResNet checkbox card. The semester-rate text already identifies the
# required fee and where it is billed.
s = re.sub(
    r'\n\s*<div class="main-campus-option">\s*<input type="checkbox" id="main-resnet-fee">.*?</div>',
    '',
    s,
    count=1,
    flags=re.S,
)
s = re.sub(
    r'(\.main-campus-comparison-options\{.*?grid-template-columns:)19fr 20fr(;)',
    r'\g<1>1fr\2',
    s,
    count=1,
    flags=re.S,
)

# ResNet is always part of the monthly equivalent; winter break remains optional.
s = s.replace("  const resnetBox=document.getElementById('main-resnet-fee');\n", '', 1)
s = s.replace("    const resnet=resnetBox && resnetBox.checked ? 150 : 0;", "    const resnet=150;", 1)
s = s.replace("    const suffix=resnet ? 'per student' : 'per student · ResNet excluded';", "    const suffix='per student';", 1)
s = s.replace("  if(resnetBox) resnetBox.addEventListener('change',renderMainCampusRates);\n", '', 1)

# Put the auditable room workbook beside the methodology link on the standalone
# price table as well as in the compact story version.
old_price_note = '''<p class="housing-monthly-note">Monthly prices. The low–high range is rounded to whole dollars. The displayed midpoint is calculated from those rounded figures so the visible arithmetic checks. Underlying analysis still uses unrounded listing values, with one vote per listing. Utilities and fees vary. <a href="references.html#rental-method">How this is calculated</a></p>'''
new_price_note = '''<p class="housing-monthly-note">Monthly prices. The low–high range is rounded to whole dollars. The displayed midpoint is calculated from those rounded figures so the visible arithmetic checks. Underlying analysis still uses unrounded listing values, with one vote per listing. Utilities and fees vary. <a href="references.html#rental-method">How this is calculated</a> · <a href="references.html#room-rent-audit">Room-listing Excel audit</a></p>'''
if old_price_note in s:
    s = s.replace(old_price_note, new_price_note, 1)
elif 'Room-listing Excel audit' not in s:
    raise SystemExit('Could not add room Excel audit link to price table')

# Guardrails for the interactive cards and residence-hall comparison.
if 'room charge only' in s:
    raise SystemExit('Affordability dropdown still says room charge only')
if "stats:{avg_low:(3970*2/9)" in s or "stats:{avg_low:(4600*2/9)" in s:
    raise SystemExit('Affordability calculation still excludes ResNet')
if 'id="main-resnet-fee"' in s:
    raise SystemExit('Main residence-hall ResNet checkbox still present')
if 'ResNet excluded' in s:
    raise SystemExit('Main residence-hall display still says ResNet excluded')
if '≈ $916/month<span>per student</span>' not in s or '≈ $1,056/month<span>per student</span>' not in s:
    raise SystemExit('Main residence-hall static figures were not updated')

p.write_text(s, encoding='utf-8')
