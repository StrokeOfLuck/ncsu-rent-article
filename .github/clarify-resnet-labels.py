from pathlib import Path

p = Path('draft-story-0915.html')
s = p.read_text(encoding='utf-8')

# The monthly figures start with ResNet excluded, so describe ResNet as a separate
# required add-on rather than visually adding it to the room charge.
s = s.replace(
    '$3,970/semester housing + $150 required ResNet fee (paid to OIT)',
    '$3,970/semester housing · Required ResNet: +$150/semester (paid to OIT)',
)
s = s.replace(
    '$4,600/semester housing + $150 required ResNet fee (paid to OIT)',
    '$4,600/semester housing · Required ResNet: +$150/semester (paid to OIT)',
)

# Make the same distinction in the embedded off-campus comparison cards.
s = s.replace(
    "note.textContent=note.textContent.replace('$150 required ResNet fee','$150 required ResNet fee (paid to OIT)');",
    "note.textContent=note.textContent.replace('$4,600/semester + $150 required ResNet fee','$4,600/semester housing · Required ResNet: +$150/semester (paid to OIT)').replace('$3,970/semester + $150 required ResNet fee','$3,970/semester housing · Required ResNet: +$150/semester (paid to OIT)').replace('$150 required ResNet fee','$150 required ResNet fee (paid to OIT)');",
)

p.write_text(s, encoding='utf-8')
