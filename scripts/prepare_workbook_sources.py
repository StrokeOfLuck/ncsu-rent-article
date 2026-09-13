import csv,json
from pathlib import Path
root=Path(__file__).resolve().parents[1]
a={key:list(csv.DictReader((root/'data'/file).open())) for key,file in [('properties','ncsu-properties.csv'),('floorplans','ncsu-floorplans.csv')]}
(root/'data/audits').mkdir(exist_ok=True)
(root/'data/audits/source-tables.json').write_text(json.dumps(a))
