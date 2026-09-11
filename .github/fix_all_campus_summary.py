from pathlib import Path
import re

index_path = Path("index.html")
refs_path = Path("references.html")

index = index_path.read_text(encoding="utf-8")

old_summary_decl = '''  const summary = overallAllCampusesSummary();
  const bandSummary = overallDistanceBandSummary(currentCampusKey);
'''
new_summary_decl = '''  const summary = overallAllCampusesSummary();
'''
if old_summary_decl not in index:
    raise SystemExit("Expected summary declaration block not found in index.html")
index = index.replace(old_summary_decl, new_summary_decl, 1)

old_card = '''  document.getElementById("combinedRentMeta").textContent =
    `${campuses[currentCampusKey].label} · equal-weight average of the 0–1, >1–3 and >3–5 mile distance-band means`;
  document.getElementById("combinedPerOverall").textContent = bandSummary.perOverall.display;
  document.getElementById("combinedPerMid").textContent = money(bandSummary.perOverall.midpoint);
  document.getElementById("combinedWholeOverall").textContent = bandSummary.wholeOverall.display;
  document.getElementById("combinedWholeMid").textContent = money(bandSummary.wholeOverall.midpoint);
'''
new_card = '''  document.getElementById("combinedRentMeta").textContent =
    `Main, Centennial and Biomedical Campus · ${summary.uniqueCount} unique listings within 5 miles of at least one campus reference · overlapping listings counted once`;
  document.getElementById("combinedPerOverall").textContent = summary.perOverall.display;
  document.getElementById("combinedPerMid").textContent = money(summary.perOverall.midpoint);
  document.getElementById("combinedWholeOverall").textContent = summary.wholeOverall.display;
  document.getElementById("combinedWholeMid").textContent = money(summary.wholeOverall.midpoint);
'''
if old_card not in index:
    raise SystemExit("Expected combined rent card block not found in index.html")
index = index.replace(old_card, new_card, 1)
index_path.write_text(index, encoding="utf-8")

refs = refs_path.read_text(encoding="utf-8")

old_fact = '''            <div class="fact-value">The overall affordability visualizer is <strong>not tied to the currently selected map campus</strong>. It pools every unique listing appearing in any Main Campus, Centennial Campus or Centennial Biomedical Campus (CVM reference view) 1-, 3- or 5-mile view, then counts each NC State Off-Campus Housing listing once before averaging rents.</div>'''
new_fact = '''            <div class="fact-value">The off-campus summary card and affordability visualizer are <strong>not tied to the currently selected map campus</strong>. They pool every unique listing within 5 miles of Main Campus, Centennial Campus or Centennial Biomedical Campus, deduplicate by NC State Off-Campus Housing listing ID, and then average the remaining unique listings. A listing near more than one campus contributes once to the combined calculation.</div>'''
if old_fact not in refs:
    raise SystemExit("Expected combined affordability fact not found in references.html")
refs = refs.replace(old_fact, new_fact, 1)

old_worked_start = '''          <strong>Worked calculation for the affordability visualizer:</strong> The nine displayed campus-radius views contain <strong>156 unique listings</strong> after deduplication by NC State Off-Campus Housing listing ID:'''
new_worked_start = '''          <strong>Worked calculation for the combined all-campus summary card and affordability visualizer:</strong> The three campus areas contain <strong>156 unique listings</strong> within 5 miles of at least one campus reference after deduplication by NC State Off-Campus Housing listing ID:'''
if old_worked_start not in refs:
    raise SystemExit("Expected worked-calculation introduction not found in references.html")
refs = refs.replace(old_worked_start, new_worked_start, 1)

old_method_sentence = '''The three 1-, 3- and 5-mile summary rows are not averaged together because those radius groups overlap and would count many of the same listings more than once.'''
new_method_sentence = '''The combined result is not made by averaging the three campus averages or the cumulative 1-, 3- and 5-mile averages. Those geographic views overlap, so averaging their means would give some listings multiple influence and would also give each campus equal weight regardless of how many unique listings it contributes.'''
if old_method_sentence not in refs:
    raise SystemExit("Expected overlap-method sentence not found in references.html")
refs = refs.replace(old_method_sentence, new_method_sentence, 1)

pattern = re.compile(
    r'''\n        <div class="use-note">\n          <strong>Worked calculation for the selected-campus off-campus summary card:</strong>.*?\n        </div>\n\n        <div class="band-math-wrap">''',
    re.S,
)
replacement = '''
        <div class="use-note">
          <strong>How the campus distance-band tables are used:</strong> The 0–1, &gt;1–3 and &gt;3–5 mile rows remain separate campus-specific comparisons. Their means are calculated directly from the listings in each non-overlapping band. They are <strong>not averaged together to create the all-campus off-campus summary</strong>. The combined card instead uses the deduplicated 156-listing union described above, so a listing that falls within multiple campus areas is counted once.
        </div>

        <div class="band-math-wrap">'''
refs, count = pattern.subn(replacement, refs, count=1)
if count != 1:
    raise SystemExit(f"Expected one selected-campus summary note, replaced {count}")

refs_path.write_text(refs, encoding="utf-8")

print("Patched index.html and references.html")
