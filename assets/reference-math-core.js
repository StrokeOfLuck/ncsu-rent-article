(function(){
  const d=RENT_DATA, A=RentAnalysis, rows=d.rentals, u=A.union(rows), s=A.summarize(u);
  const mainRows=A.campus(rows,'main').filter(r=>r.pricing_type==='Per bedroom'&&A.valid(r));
  const main=A.stats(mainRows);
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
        <div class="evidence" style="margin-top:14px"><img src="assets/housing-insecurity-11-3-evidence.svg" alt="Recreated excerpt from the March 2024 NC State report showing the housing insecurity question and Table 3, where 153 of 1,354 students, or 11.3 percent, were housing insecure."><div class="caption"><strong>Readable recreation.</strong> Recreated from the report's housing insecurity definition and Table 3.</div></div>
        <div class="evidence" style="margin-top:14px">
          <a href="https://packessentials.dasa.ncsu.edu/food-and-housing-insecurity-at-nc-state/" target="_blank" rel="noopener noreferrer"><img src="assets/references/haskett-table-3-original.png?v=20260920-original" alt="Original Table 3 from the March 2024 NC State food and housing insecurity report, showing food security, housing security and experienced homelessness results."></a>
          <div class="caption"><strong>Original Table 3.</strong> Saved from the March 2024 NC State report. Select the image to open NC State's current Campus Reports page.</div>
        </div>
        <p><a href="https://doi.org/10.31234/osf.io/t46jv" target="_blank" rel="noopener noreferrer">Mary E. Haskett, Homelessness and Food &amp; Housing Insecurity among College Students: Third Wave</a> · March 2024 NC State report, 2023 survey data.</p>
        <div class="use-note"><strong>Reporting note:</strong> This article uses the 11.3% housing insecurity measure because it directly asks about students' confidence in paying for their current housing. It does not use the report's 14% homelessness figure as a direct affordability measure. That measure counts any of nine qualifying housing situations at any point during the previous 12 months, including temporary couch surfing, and the report does not establish a minimum duration.</div>
      </div>`;
  }

  function worked(v) {
    return `<ol><li>Low-price sum: ${usd(v.low_sum)} ÷ ${v.n} = <strong>${usd(v.avg_low)}</strong>.</li><li>High-price sum: ${usd(v.high_sum)} ÷ ${v.n} = <strong>${usd(v.avg_high)}</strong>.</li><li>Midpoint sum: (${usd(v.low_sum)} + ${usd(v.high_sum)}) ÷ 2 = ${usd((v.low_sum+v.high_sum)/2)}. Divide by ${v.n} = <strong>${usd(v.midpoint)}</strong>.</li><li>Median of the ${v.n} listing midpoints: <strong>${usd(v.median_midpoint)}</strong>.</li></ol>`;
  }
  document.getElementById('worked-whole').innerHTML='<h2>Whole-unit calculation, outside the article’s room scope</h2>'+worked(s.wholeOverall);

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

`);
  }
})();