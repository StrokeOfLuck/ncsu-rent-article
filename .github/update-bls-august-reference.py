from pathlib import Path

p = Path("references.html")
s = p.read_text(encoding="utf-8")

old = '''<article class="ref" id="bls-housing-cpi-benchmarks"><div class="ref-head"><div><div class="ref-no">National price context</div><div class="ref-title">July 2026 CPI benchmarks, with a fixed release link</div></div></div><div class="ref-body">
<p>The <a href="https://www.bls.gov/news.release/archives/cpi_08122026.htm">BLS July 2026 CPI release, published August 12, 2026</a> reports July-to-July increases of 3.0% for lodging while at school, 2.9% for rent of primary residence and 3.4% for all items. The article intentionally uses this fixed July comparison; a rolling “latest release” link would eventually point to a different month.</p>
<p><a href="https://www.bls.gov/cpi/additional-resources/entry-level-item-descriptions.htm">BLS category definitions</a>: lodging while at school covers college/university owned, leased or controlled housing. Merely advertising a private rental on the NC State referral portal does not put it in that CPI category. Rent of primary residence is the closer national comparison for private off-campus rents. These national twelve-month changes provide context; they do not estimate NC State’s local rent inflation or explain an individual room-rate increase.</p>
</div></article>'''

new = '''<article class="ref" id="bls-housing-cpi-benchmarks"><div class="ref-head"><div><div class="ref-no">National price context</div><div class="ref-title">August 2026 CPI benchmarks, with a fixed release link</div></div></div><div class="ref-body">
<p>The <a href="https://www.bls.gov/news.release/archives/cpi_09112026.htm">BLS August 2026 CPI release, published September 11, 2026</a> reports August-to-August increases of <strong>3.1% for lodging while at school</strong>, 2.7% for rent of primary residence and 3.4% for all items. The reference uses this fixed August comparison; a rolling “latest release” link would eventually point to a different month.</p>
<p><a href="https://www.bls.gov/cpi/additional-resources/entry-level-item-descriptions.htm">BLS category definitions</a>: lodging while at school covers college/university owned, leased or controlled housing. Merely advertising a private rental on the NC State referral portal does not put it in that CPI category. Rent of primary residence is the closer national comparison for private off-campus rents. These national twelve-month changes provide context; they do not estimate NC State’s local rent inflation or explain an individual room-rate increase.</p>
<div class="use-note"><strong>Reporting note:</strong> The draft graphic shown to University Housing during the Sept. 15 interview used the July 2026 lodging-while-at-school figure of 3.0%. This reference was updated to the newer August 2026 BLS reading of 3.1%. Housing officials should not be characterized as having responded specifically to the 3.1% figure.</div>
</div></article>'''

if old not in s:
    raise SystemExit("Expected July 2026 BLS reference block not found; no changes made.")

p.write_text(s.replace(old, new, 1), encoding="utf-8")
