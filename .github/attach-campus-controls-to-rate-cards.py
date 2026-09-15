from pathlib import Path

p = Path('draft-story-0915.html')
s = p.read_text(encoding='utf-8')

# The winter-break and ResNet controls affect only the two on-campus cards.
# Keep the off-campus mean card at the left, and attach the controls directly
# above the single and double cards on the right.
s = s.replace(
    "          strip.parentNode.insertBefore(breakRow,strip);",
    "          strip.insertBefore(breakRow, strip.children[1] || null);",
    1,
)

marker = '''            @media(max-width:700px){'''
overrides = '''            /* Attach campus-only controls to the two residence-hall cards. */
            .draft-comparison-strip > *:nth-child(1){
              grid-column:1;
              grid-row:1 / span 2;
              border-top:1px solid var(--line) !important;
              border-bottom:1px solid var(--line) !important;
            }
            .draft-comparison-strip > .draft-campus-break-row{
              grid-column:2 / 4 !important;
              grid-row:1;
              margin:0 !important;
              padding:0 !important;
              border-top:1px solid var(--line) !important;
              border-bottom:1px solid var(--line) !important;
              border-left:1px solid var(--line) !important;
              border-right:0 !important;
              background:#fff !important;
            }
            .draft-comparison-strip > *:nth-child(3){
              grid-column:2;
              grid-row:2;
              border-bottom:1px solid var(--line) !important;
            }
            .draft-comparison-strip > *:nth-child(4){
              grid-column:3;
              grid-row:2;
              border-bottom:1px solid var(--line) !important;
              border-right:0 !important;
            }
            .draft-comparison-strip .draft-campus-break-control{
              grid-column:1 / -1;
              border-left:0;
            }

            @media(max-width:700px){
              .draft-comparison-strip > *:nth-child(1),
              .draft-comparison-strip > .draft-campus-break-row,
              .draft-comparison-strip > *:nth-child(3),
              .draft-comparison-strip > *:nth-child(4){
                grid-column:1 !important;
                grid-row:auto !important;
              }
              .draft-comparison-strip > .draft-campus-break-row{
                border-left:0 !important;
              }
'''

if 'Attach campus-only controls to the two residence-hall cards.' not in s:
    if marker not in s:
        raise SystemExit('Could not find comparison mobile breakpoint')
    s = s.replace(marker, overrides, 1)

p.write_text(s, encoding='utf-8')
