from pathlib import Path

p = Path('draft-story-0915.html')
s = p.read_text(encoding='utf-8')

old_method = '''Projected 2026–27 residence hall rates from official housing rates, converted from two semester charges to a 9-month academic-year monthly equivalent. By default, the comparison shows the University Housing room charge alone. Residents also pay a required $150-per-semester ResNet fee for internet access, which goes to OIT rather than University Housing; use the ResNet checkbox below to add it.'''
new_method = '''Projected 2026–27 residence hall rates from official housing rates, converted from two semester charges to a 9-month academic-year monthly equivalent. The calculation includes the required $150-per-semester ResNet fee for internet access, which residents must pay but which goes to OIT rather than University Housing. The ResNet checkbox is checked by default; turn it off only to view the University Housing room charge by itself.'''
s = s.replace(old_method, new_method, 1)

s = s.replace('id="resnet-fee">', 'id="resnet-fee" checked>', 1)
s = s.replace('≈ $882/month', '≈ $916/month', 1)
s = s.replace('≈ $1,022/month', '≈ $1,056/month', 1)

s = s.replace(
    '<label for="resnet-fee"><strong>Required ResNet (+$150/semester; ≈ +$33/month)</strong> <span class="break-note">Paid to OIT for internet access.</span></label>',
    '<label for="resnet-fee"><strong>Required ResNet (+$150/semester; ≈ +$33/month)</strong> <span class="break-note">Required fee paid to OIT for internet access; included by default.</span></label>',
    1,
)

p.write_text(s, encoding='utf-8')
