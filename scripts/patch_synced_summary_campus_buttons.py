from pathlib import Path

index_path = Path("index.html")
refs_path = Path("references.html")

text = index_path.read_text(encoding="utf-8")

# 1) Add compact campus controls to the off-campus summary card.
old_markup = '''        <div class="housing-section-head housing-section-first">
          <div>
            <div class="housing-section-kicker">Off campus listings</div>
            <div class="housing-section-title">Advertised rents from NC State’s Off-Campus Housing site</div>
          </div>
        </div>'''
new_markup = '''        <div class="housing-section-head housing-section-first">
          <div>
            <div class="housing-section-kicker">Off campus listings</div>
            <div class="housing-section-title">Advertised rents from NC State’s Off-Campus Housing site</div>
          </div>
          <div class="summary-campus-buttons" aria-label="Campus rent summary selector">
            <button id="summary-btn-main" class="campus-btn active" type="button" onclick="setCampus('main')">Main</button>
            <button id="summary-btn-centennial" class="campus-btn" type="button" onclick="setCampus('centennial')">Centennial</button>
            <button id="summary-btn-vet" class="campus-btn" type="button" onclick="setCampus('vet')">Biomedical</button>
          </div>
        </div>'''
if old_markup in text and 'id="summary-btn-main"' not in text:
    text = text.replace(old_markup, new_markup, 1)

# 2) Make the initial summary note match the selected-campus calculation immediately.
text = text.replace(
    '<span id="combinedRentMeta">Main, Centennial and Biomedical Campus · all unique listings across the displayed 1-, 3- and 5-mile views, counted once</span>',
    '<span id="combinedRentMeta">Main Campus · equal-weight average of the 0–1, &gt;1–3 and &gt;3–5 mile distance-band means</span>',
    1,
)

# 3) Keep both sets of campus controls visibly synchronized.
old_sync = '''  document.querySelectorAll(".campus-btn").forEach(b=>b.classList.remove("active"));
  document.getElementById("btn-" + key).classList.add("active");'''
new_sync = '''  document.querySelectorAll(".campus-btn").forEach(b=>b.classList.remove("active"));
  document.getElementById("btn-" + key)?.classList.add("active");
  document.getElementById("summary-btn-" + key)?.classList.add("active");'''
if old_sync in text:
    text = text.replace(old_sync, new_sync, 1)

# 4) Add layout rules for the mirrored controls.
css = r'''

/* Synced campus controls in the off-campus rent summary */
.summary-campus-buttons{
  display:grid;
  grid-template-columns:repeat(3,minmax(0,1fr));
  gap:7px;
  width:min(360px,100%);
  margin-left:auto;
}
.summary-campus-buttons .campus-btn{
  min-width:0;
  padding:7px 10px;
  font-size:10.5px;
}
@media(max-width:700px){
  .housing-section-first{
    align-items:stretch;
  }
  .summary-campus-buttons{
    width:100%;
    margin-left:0;
  }
  .summary-campus-buttons .campus-btn{
    padding:7px 5px;
    font-size:10px;
  }
}
'''
if '.summary-campus-buttons{' not in text:
    text = text.replace('</style>', css + '\n</style>', 1)

index_path.write_text(text, encoding="utf-8")

refs = refs_path.read_text(encoding="utf-8")
needle = '<strong>Worked calculation for the selected-campus off-campus summary card:</strong> The card beneath the distance-band table gives the three non-overlapping bands equal weight.'
replacement = '<strong>Worked calculation for the selected-campus off-campus summary card:</strong> The Main, Centennial and Biomedical buttons on this card are synchronized with the campus selector above the map. The card always shows the selected campus only; it does not combine the three campus averages. The card beneath the distance-band table gives the three non-overlapping bands equal weight.'
if needle in refs and 'The card always shows the selected campus only; it does not combine the three campus averages.' not in refs:
    refs = refs.replace(needle, replacement, 1)
refs_path.write_text(refs, encoding="utf-8")

print("Patched synced campus controls and methodology note.")
