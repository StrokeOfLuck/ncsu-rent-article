from pathlib import Path

path = Path("references.html")
text = path.read_text(encoding="utf-8")

old_header = '<thead><tr><th>Campus</th><th>Distance band</th><th>Properties</th><th>Per bedroom low: sum ÷ n = mean</th><th>Per bedroom high: sum ÷ n = mean</th><th>Whole unit low: sum ÷ n = mean</th><th>Whole unit high: sum ÷ n = mean</th></tr></thead>'
new_header = '<thead><tr><th>Campus</th><th>Distance band</th><th>Properties</th><th>Numeric rents used</th><th>Per bedroom low: sum ÷ n = mean</th><th>Per bedroom high: sum ÷ n = mean</th><th>Whole unit low: sum ÷ n = mean</th><th>Whole unit high: sum ÷ n = mean</th></tr></thead>'
assert text.count(old_header) == 1, "Expected one band table header"
text = text.replace(old_header, new_header, 1)

rows = {
    '<tr><td>Main Campus</td><td>0–1 mi</td><td>54</td>': '<tr><td>Main Campus</td><td>0–1 mi</td><td>54</td><td>54 of 54</td>',
    '<tr><td>Main Campus</td><td>>1–3 mi</td><td>73</td>': '<tr><td>Main Campus</td><td>>1–3 mi</td><td>73</td><td><strong>72 of 73</strong></td>',
    '<tr><td>Main Campus</td><td>>3–5 mi</td><td>26</td>': '<tr><td>Main Campus</td><td>>3–5 mi</td><td>26</td><td>26 of 26</td>',
    '<tr><td>Centennial Campus</td><td>0–1 mi</td><td>29</td>': '<tr><td>Centennial Campus</td><td>0–1 mi</td><td>29</td><td>29 of 29</td>',
    '<tr><td>Centennial Campus</td><td>>1–3 mi</td><td>96</td>': '<tr><td>Centennial Campus</td><td>>1–3 mi</td><td>96</td><td><strong>95 of 96</strong></td>',
    '<tr><td>Centennial Campus</td><td>>3–5 mi</td><td>26</td>': '<tr><td>Centennial Campus</td><td>>3–5 mi</td><td>26</td><td>26 of 26</td>',
    '<tr><td>Centennial Biomedical Campus</td><td>0–1 mi</td><td>10</td>': '<tr><td>Centennial Biomedical Campus</td><td>0–1 mi</td><td>10</td><td>10 of 10</td>',
    '<tr><td>Centennial Biomedical Campus</td><td>>1–3 mi</td><td>92</td>': '<tr><td>Centennial Biomedical Campus</td><td>>1–3 mi</td><td>92</td><td>92 of 92</td>',
    '<tr><td>Centennial Biomedical Campus</td><td>>3–5 mi</td><td>44</td>': '<tr><td>Centennial Biomedical Campus</td><td>>3–5 mi</td><td>44</td><td><strong>43 of 44</strong></td>',
}
for old, new in rows.items():
    assert text.count(old) == 1, f"Expected one row start: {old}"
    text = text.replace(old, new, 1)

marker = '''        <div class="filter-note">
          <strong>Cumulative-radius audit:</strong>'''
note = '''        <div class="filter-note">
          <strong>Numeric-rent count:</strong> “Properties” counts every listing in each distance band. “Numeric rents used” counts listings with numeric low/high rent values used in the sums and means. Three rows are short by one: <strong>Main Campus &gt;1–3 miles (72 of 73)</strong>, <strong>Centennial Campus &gt;1–3 miles (95 of 96)</strong>, and <strong>Centennial Biomedical Campus &gt;3–5 miles (43 of 44)</strong>. All three gaps are the same listing, <strong>Lofts at Lineberry</strong>, which was advertised as <strong>“Call for Pricing”</strong> with no numeric rent in the Sept. 9, 2026 collection. It remains in each band’s property total but is excluded from rent sums and means and is not treated as $0.
        </div>
        <div class="filter-note">
          <strong>Cumulative-radius audit:</strong>'''
assert text.count(marker) == 1, "Expected one cumulative-radius note marker"
text = text.replace(marker, note, 1)

text = text.replace('.band-math-table{min-width:1180px', '.band-math-table{min-width:1280px', 1)
path.write_text(text, encoding="utf-8")
