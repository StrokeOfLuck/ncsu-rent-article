from pathlib import Path

p = Path('draft-story-0915.html')
s = p.read_text(encoding='utf-8')

s = s.replace(
    '<span class="draft-campus-resnet-note">Paid to OIT</span>',
    '<span class="draft-campus-resnet-note">Paid to OIT for internet access.</span>'
)

s = s.replace(
    '''            .draft-campus-resnet-note{
              color:#746f68;
              white-space:nowrap;
            }''',
    '''            .draft-campus-resnet-note{
              color:#746f68;
              white-space:normal;
              line-height:1.25;
              flex:0 1 auto;
            }'''
)

p.write_text(s, encoding='utf-8')
