from pathlib import Path


def patch(path, replacements):
    p = Path(path)
    s = p.read_text(encoding="utf-8")
    old_s = s
    for old, new in replacements:
        s = s.replace(old, new)
    if s != old_s:
        p.write_text(s, encoding="utf-8")


patch("references.html", [
    (
        "Over the 12 months ending July 2026, <strong>lodging while at school increased 3.0%</strong>, <strong>rent of primary residence increased 2.9%</strong>, and the <strong>all-items CPI-U increased 3.4%</strong>. <a href=\"https://www.bls.gov/news.release/archives/cpi_08122026.htm\"",
        "Over the 12 months ending August 2026, <strong>lodging while at school increased 3.1%</strong>, <strong>rent of primary residence increased 2.7%</strong>, and the <strong>all-items CPI-U increased 3.4%</strong>. <a href=\"https://www.bls.gov/news.release/archives/cpi_09112026.htm\""
    ),
])

patch("draft-story-0915.html", [
    (
        "Its published projections show that eight of 10 housing options are expected to increase faster than the 3.0% average for the Bureau of Labor Statistics’ lodging-while-at-school measure.",
        "Its published projections show that eight of 10 housing options are expected to increase faster than the 3.1% 12-month increase in the Bureau of Labor Statistics’ lodging-while-at-school index from August 2025 to August 2026."
    ),
])

patch("index.html", [
    ("with July 2026 BLS 12-month price benchmarks.", "with August 2026 BLS 12-month price benchmarks."),
    ("housing-rate-benchmark-line.benchmark-rent{\n  left:36.25%;", "housing-rate-benchmark-line.benchmark-rent{\n  left:33.75%;"),
    ("housing-rate-benchmark-line.benchmark-school{\n  left:37.5%;", "housing-rate-benchmark-line.benchmark-school{\n  left:38.75%;"),
    ("style=\"left:37.5%\"><span class=\"housing-rate-active-name\">Lodging while at school</span><span class=\"housing-rate-active-pct\">3.0%</span>", "style=\"left:38.75%\"><span class=\"housing-rate-active-name\">Lodging while at school</span><span class=\"housing-rate-active-pct\">3.1%</span>"),
    ("Show BLS lodging while at school, 3.0 percent, on the chart", "Show BLS lodging while at school, 3.1 percent, on the chart"),
    ("<strong>+3.0%</strong><span>July 2025 to July 2026</span>", "<strong>+3.1%</strong><span>August 2025 to August 2026</span>"),
    ("Show BLS rent of primary residence, 2.9 percent, on the chart", "Show BLS rent of primary residence, 2.7 percent, on the chart"),
    ("<strong>+2.9%</strong><span>July 2025 to July 2026</span>", "<strong>+2.7%</strong><span>August 2025 to August 2026</span>"),
    ("<strong>+3.4%</strong><span>July 2025 to July 2026</span>", "<strong>+3.4%</strong><span>August 2025 to August 2026</span>"),
    ("https://www.bls.gov/news.release/archives/cpi_08122026.htm", "https://www.bls.gov/news.release/archives/cpi_09112026.htm"),
    ("school: { name: 'Lodging while at school', pct: '3.0%', left: '37.5%' }", "school: { name: 'Lodging while at school', pct: '3.1%', left: '38.75%' }"),
    ("rent:   { name: 'Rent of primary residence', pct: '2.9%', left: '36.25%' }", "rent:   { name: 'Rent of primary residence', pct: '2.7%', left: '33.75%' }"),
])
