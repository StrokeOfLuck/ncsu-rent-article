from pathlib import Path

# Match the draft lede typeface to the article body while preserving its slightly larger size.
draft = Path('draft-story-0915.html')
s = draft.read_text(encoding='utf-8')
marker = '/* Lede/body type consistency */'
if marker not in s:
    css = '''\n\n/* Lede/body type consistency */\n.lede{\n  font-family:Georgia, \"Times New Roman\", serif;\n  line-height:1.45;\n}\n/* End lede/body type consistency */\n'''
    s = s.replace('</style>', css + '\n</style>', 1)
    draft.write_text(s, encoding='utf-8')

# Keep the need-based aid titles on one line at desktop widths without colliding
# with the annual award amount. Narrow screens keep the existing responsive stack.
index = Path('index.html')
s = index.read_text(encoding='utf-8')
marker = '/* Aid title collision fix */'
if marker not in s:
    css = '''\n\n/* Aid title collision fix */\n@media (min-width:701px){\n  .aid-copy{\n    grid-template-columns:minmax(150px,1fr) auto;\n    column-gap:12px;\n  }\n  .aid-name{\n    white-space:nowrap;\n    font-size:12px;\n    line-height:1.2;\n  }\n  .aid-annual{\n    white-space:nowrap;\n    font-size:18px;\n  }\n}\n/* End aid title collision fix */\n'''
    s = s.replace('</style>', css + '\n</style>', 1)
    index.write_text(s, encoding='utf-8')
