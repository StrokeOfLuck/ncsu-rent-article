(function(){
  const d=RENT_DATA, A=RentAnalysis, rows=d.rentals, u=A.union(rows), s=A.summarize(u);
  const main=A.summarize(A.campus(rows,'main')).perOverall;
  const label=key=>key==='vet'?'Biomedical Campus':d.campuses[key].label;
  const esc=x=>String(x??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const usd=x=>x==null?'—':x.toLocaleString('en-US',{style:'currency',currency:'USD',minimumFractionDigits:2,maximumFractionDigits:2});
  const pct=x=>x.toFixed(2)+'%';
  const table=(headers,rs)=>'<table class="method-table"><thead><tr>'+headers.map(x=>'<th>'+x+'</th>').join('')+'</tr></thead><tbody>'+rs.map(r=>'<tr>'+r.map(x=>'<td>'+x+'</td>').join('')+'</tr>').join('')+'</tbody></table>';

  const housingRef=document.getElementById('student-housing-insecurity-2024');
  if(housingRef){
    housingRef.innerHTML=`
      <div class="ref-head"><div><div class="ref-no">Housing insecurity and support</div><div class="ref-title">March 2024 NC State food and housing insecurity report</div></div></div>
      <div class="ref-body">
        <h2>Highlighted housing insecurity measure</h2>
        <blockquote class="survey-highlight">Housing insecurity was measured by whether students were confident they could pay for their current housing through the end of the school year.</blockquote>
        <div class="facts" style="margin-top:12px">
          <div class="fact"><div class="fact-label">Housing insecure</div><div class="fact-value"><strong>11.3%</strong> · 153 of 1,354 respondents</div></div>
          <div class="fact"><div class="fact-label">Survey question</div><div class="fact-value">“Are you confident about your ability to pay for the place you're currently staying, so you can remain there at least until the end of the school year?”</div></div>
        </div>
        <div class="evidence" style="margin-top:14px"><img src="assets/housing-insecurity-11-3-evidence.svg" alt="Recreated excerpt from the March 2024 NC State report showing the housing insecurity question and Table 3, where 153 of 1,354 students, or 11.3 percent, were housing insecure."><div class="caption">Recreated from the report's housing insecurity definition and Table 3. The linked source contains the original report.</div></div>
        <p><a href="https://doi.org/10.31234/osf.io/t46jv" target="_blank" rel="noopener noreferrer">Mary E. Haskett, Homelessness and Food &amp; Housing Insecurity among College Students: Third Wave</a> · March 2024 NC State report, 2023 survey data.</p>
        <div class="use-note"><strong>Reporting note:</strong> This article uses the 11.3% housing insecurity measure because it directly asks about students' confidence in paying for their current housing. It does not use the report's 14% homelessness figure as a direct affordability measure. That measure counts any of nine qualifying housing situations at any point during the previous 12 months, including temporary couch surfing, and the report does not establish a minimum duration.</div>
      </div>`;
  }

  document.getElementById('sample-flow').innerHTML=`<strong>Room-only selection:</strong> ${rows.length} saved listing IDs = ${s.perOverall.n} included room listings + ${rows.length-s.perOverall.n} outside the room article. The latter comprise ${rows.length-u.length} outside all three five-mile areas, ${s.wholeOverall.n} usable whole-unit offers inside the areas, and ${s.excluded} inside-area records with unusable or unresolved prices. Each ID is counted once in this reconciliation.`;
  const countRows=Object.keys(d.campuses).map(key=>{
    const v=A.summarize(A.campus(rows,key)).perOverall;
    const bands=[[0,1],[1,3],[3,5]].map(([lo,hi])=>A.summarize(A.campus(rows,key,lo,hi)).perOverall.n);
    return [esc(label(key)),...bands,v.n,usd(v.midpoint)];
  });
  document.getElementById('count-reconciliation').innerHTML=table(['Campus','0–1 mi','>1–3 mi','>3–5 mi','Total rooms','Mean midpoint'],countRows);
  const roomBands=[[0,1],[1,3],[3,5]].map(([lo,hi])=>A.summarize(A.campus(rows,'main',lo,hi)).perOverall);
  document.getElementById('weighting-math').innerHTML=`<strong>Main Campus example:</strong> ${roomBands.map(b=>b.n).join(' + ')} = ${main.n} room listings. Their individual midpoints add to ${usd((main.low_sum+main.high_sum)/2)}. Divide by ${main.n} for a mean of <strong>${usd(main.midpoint)}</strong>. Band contributions reflect the number of advertisements, not student demand.`;
  function worked(v) {
    return `<ol><li>Low-price sum: ${usd(v.low_sum)} ÷ ${v.n} = <strong>${usd(v.avg_low)}</strong>.</li><li>High-price sum: ${usd(v.high_sum)} ÷ ${v.n} = <strong>${usd(v.avg_high)}</strong>.</li><li>Midpoint sum: (${usd(v.low_sum)} + ${usd(v.high_sum)}) ÷ 2 = ${usd((v.low_sum+v.high_sum)/2)}. Divide by ${v.n} = <strong>${usd(v.midpoint)}</strong>.</li><li>Median of the ${v.n} listing midpoints: <strong>${usd(v.median_midpoint)}</strong>.</li></ol>`;
  }
  document.getElementById('worked-union').innerHTML=worked(s.perOverall);
  document.getElementById('worked-whole').innerHTML='<h2>Whole-unit calculation, outside the article’s room scope</h2>'+worked(s.wholeOverall);
  const br=[];
  for(const key of Object.keys(d.campuses)) for(const [inner,outer,band] of [[0,1,'0–1 mi'],[1,3,'>1–3 mi'],[3,5,'>3–5 mi'],[0,5,'Pooled 0–5 mi']]) {
    const a=A.summarize(A.campus(rows,key,inner,outer)).perOverall;
    br.push([esc(label(key)),band,a.n,usd(a.low_sum),usd(a.high_sum),usd(a.avg_low),usd(a.avg_high),usd(a.midpoint)]);
  }
  document.getElementById('band-math').innerHTML=table(['Campus','Distance','Rooms used','Low sum','High sum','Mean low','Mean high','Mean midpoint'],br);

  const selections=[['Primary room sample',u],['Omit all-2027-or-later offers',u.filter(r=>!r.all_2027_or_later)],['Omit waitlist mentions',u.filter(r=>!r.flags.includes('waitlist_mentioned'))],['Omit flagged Centennial Ridge endpoint',u.filter(r=>r.site_id!=='7e6kx1w')],['Apply all three omissions',u.filter(r=>!r.all_2027_or_later&&!r.flags.includes('waitlist_mentioned')&&r.site_id!=='7e6kx1w')]];
  document.getElementById('sensitivity-math').innerHTML='<p>These checks use the combined room sample across all three campus areas, counting each ID once.</p>'+table(['Scenario','Rooms used','Mean midpoint','Median midpoint'],selections.map(([name,set])=>{const v=A.summarize(set).perOverall;return [name,v.n,usd(v.midpoint),usd(v.median_midpoint)];}));
  document.getElementById('review-log').innerHTML=table(['ID / original listing','Original basis','Reviewed basis','Price status','Reason / evidence'],rows.filter(r=>!r.eligible_price||r.pricing_type!==r.original_pricing_type||r.flags.includes('high_endpoint_review')).map(r=>[`<a href="${esc(r.listing_url)}">${esc(r.site_id)} · ${esc(r.name)}</a>`,esc(r.original_pricing_type),esc(r.pricing_type),esc(r.review_status),esc(r.review_note)]));

  document.getElementById('budget-worked').innerHTML=`<strong>Default article example, Main Campus:</strong> ${usd(main.midpoint)} mean room midpoint ÷ $1,300.00 monthly gross wages × 100 = <strong>${pct(main.midpoint/1300*100)}</strong> at $15/hour and 20 hours/week. At $7.25/hour it is <strong>${pct(main.midpoint/(7.25*20*52/12)*100)}</strong>. These percentages use unrounded values and assume 52 paid weeks. The ${usd(main.median_midpoint)} median is retained as a check; the article displays the mean.`;
  const aidRows=[];
  for(const wage of [7.25,15]) for(const [name,grant,loan] of [['Work only',false,false],['Work + grant',true,false],['Work + loan',false,true],['Work + both',true,true]]) {
    const r=A.resources({wage,hours:20,...A.aidPreset({includeGrant:grant,includeLoan:loan})});
    aidRows.push([`$${wage}/hour`,name,usd(r.pay),usd(r.grant),usd(r.loan),usd(r.total),pct(main.midpoint/r.total*100)]);
  }
  document.getElementById('aid-presets-math').innerHTML=table(['Wage at 20 hours/week','Selection','Gross pay','Grant equivalent','Borrowed funds','Total resources','Main room mean ÷ resources'],aidRows);
  document.getElementById('report-wording').innerHTML=`<strong>A supported description:</strong> The ${main.n} usable room/per-bedroom advertisements within five straight-line miles of the Main Campus reference point had a mean listing midpoint of ${usd(main.midpoint)} in the September 9 snapshot. That is ${pct(main.midpoint/1300*100)} of gross wages at $15/hour and 20 hours/week in a steady, year-round work example. This describes the portal sample and a wage comparison, not how many NC State students can afford housing.`;

  const refsContainer=document.querySelector('.refs');
  if(refsContainer){
    refsContainer.insertAdjacentHTML('beforeend', `
<article class="ref" id="ncsu-local-market-housing-comparison">
  <div class="ref-head">
    <div>
      <div class="ref-no">Reference 16</div>
      <div class="ref-title">NC State Board of Trustees: Local Market Student Housing Rental Rate Comparison</div>
    </div>
    <div class="tags">
      <span class="tag">Primary source</span>
      <span class="tag">NC State</span>
      <span class="tag">Housing market</span>
      <span class="tag">Board of Trustees</span>
    </div>
  </div>
  <div class="ref-body">
    <div class="meta-grid">
      <div class="meta-label">Committee</div>
      <div class="meta-value">NC State Board of Trustees, Audit, Risk Management and Finance Committee</div>
      <div class="meta-label">Document</div>
      <div class="meta-value">November 2025 committee meeting book, Cates West presentation</div>
      <div class="meta-label">Relevant page</div>
      <div class="meta-value">PDF page 36</div>
      <div class="meta-label">Source</div>
      <div class="meta-value"><a href="https://leadership.ncsu.edu/wp-content/uploads/sites/2/2025/11/Meeting-Book-November-2025-Audit-Risk-Management-and-Finance-Committee-Meeting-2.pdf#page=36" target="_blank" rel="noopener noreferrer">Local Market Student Housing Rental Rate Comparison</a></div>
    </div>
    <hr class="rule">
    <h2>Highlighted comparison</h2>
    <div class="facts">
      <div class="fact"><div class="fact-label">2025–26 NC State apartments</div><div class="fact-value"><strong>$11,000</strong></div></div>
      <div class="fact"><div class="fact-label">2025–26 off-campus apartments</div><div class="fact-value"><strong>$13,151</strong></div></div>
      <div class="fact"><div class="fact-label">Reported cost difference</div><div class="fact-value"><strong>$2,151</strong>, or <strong>19.6%</strong> lower for NC State apartments in the university comparison.</div></div>
      <div class="fact"><div class="fact-label">Projection assumption</div><div class="fact-value">The slide assumes <strong>4% annual rate increases for peer institutions</strong>.</div></div>
    </div>
    <div class="citation" style="margin-top:12px">“University Housing remains well positioned in the local market throughout the project duration.”</div>
    <div class="use-note"><strong>Reporting note:</strong> This is NC State's own market comparison, not the September 2026 room-listing sample used in this article. The slide compares apartment costs and explicitly notes that the local market requires a 12-month lease.</div>
  </div>
</article>

<article class="ref" id="ncsu-housing-weighted-increase-2026-27">
  <div class="ref-head">
    <div>
      <div class="ref-no">Reference 17</div>
      <div class="ref-title">NC State Board of Trustees: 5% Weighted Average Housing Rate Increase for 2026–27</div>
    </div>
    <div class="tags">
      <span class="tag">Primary source</span>
      <span class="tag">NC State</span>
      <span class="tag">Housing rates</span>
      <span class="tag">Board of Trustees</span>
    </div>
  </div>
  <div class="ref-body">
    <div class="meta-grid">
      <div class="meta-label">Committee</div>
      <div class="meta-value">NC State Board of Trustees, University Affairs Committee</div>
      <div class="meta-label">Minutes</div>
      <div class="meta-value">November 13, 2025 open-session minutes, reproduced in the February 2026 meeting book</div>
      <div class="meta-label">Relevant page</div>
      <div class="meta-value">PDF page 7, minutes page 2</div>
      <div class="meta-label">Source</div>
      <div class="meta-value"><a href="https://leadership.ncsu.edu/wp-content/uploads/sites/2/2026/02/Meeting-Book-February-2026-University-Affairs-Committee-Meeting.pdf#page=7" target="_blank" rel="noopener noreferrer">University Affairs Committee meeting book</a></div>
    </div>
    <hr class="rule">
    <h2>Highlighted finding</h2>
    <div class="citation">“Regarding university housing rates, the proposed increase on a weighted average basis is 5%.”</div>
    <div class="facts" style="margin-top:12px">
      <div class="fact"><div class="fact-label">Housing increase</div><div class="fact-value"><strong>5%</strong> proposed weighted-average increase for 2026–27.</div></div>
      <div class="fact"><div class="fact-label">University explanation</div><div class="fact-value">Housing and dining are described as self-supporting programs, with higher costs tied to labor-market pressure, inflation and capital investment needs.</div></div>
      <div class="fact"><div class="fact-label">Board action</div><div class="fact-value">The committee motion recommending approval of the 2026–27 housing and dining rate requests to the full board passed.</div></div>
    </div>
    <div class="use-note"><strong>Reporting note:</strong> The 5% figure is a weighted average across University Housing, not a 5% increase for every room type. The individual rate schedule above shows increases that vary by housing type.</div>
  </div>
</article>`);
  }
})();