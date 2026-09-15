(function(){
  const housingCard=document.getElementById('ncsu-housing-rates-2026-27');
  if(!housingCard || housingCard.querySelector('.winter-break-evidence')) return;
  const body=housingCard.querySelector('.ref-body');
  if(!body) return;
  body.insertAdjacentHTML('beforeend', `
    <hr class="rule">
    <h2>Winter break is separately priced</h2>
    <div class="evidence winter-break-evidence">
      <img src="assets/winter-break-housing-costs.svg" alt="NC State Summer and Transition Housing Costs table showing Winter Break Housing at $15 per night for 2025 and projected 2026.">
      <div class="caption">Recreated from NC State Housing's Summer and Transition Housing Costs table. Winter Break Housing is listed separately at <strong>$15 per night</strong>.</div>
    </div>
    <div class="use-note"><strong>Reporting note:</strong> For most residents, winter break is not included in the fall + spring housing agreement. The 2026–27 Housing Agreement defines the academic year as fall and spring semesters, excluding winter break and summer, and says Winter Break housing is a separate term with an additional charge. E.S. King and Western Manor term agreements are exceptions, except for specified E.S. King undergraduate buildings.</div>
    <p><a href="https://housing.dasa.ncsu.edu/wp-content/uploads/sites/30/2025/12/University-Housing-Agreement-2026-2027.pdf" target="_blank" rel="noopener noreferrer">2026–27 University Housing Agreement</a></p>

    <h3>Latest published full-break example: 2025–26</h3>
    <div class="facts">
      <div class="fact"><div class="fact-label">Published winter-break request period</div><div class="fact-value"><strong>Dec. 14, 2025 to Jan. 8, 2026</strong></div></div>
      <div class="fact"><div class="fact-label">Published full-break charge</div><div class="fact-value"><strong>$360</strong> at <strong>$15/night</strong></div></div>
      <div class="fact"><div class="fact-label">Charged-night equivalent</div><div class="fact-value"><strong>$360 ÷ $15 = 24 nights</strong></div></div>
      <div class="fact"><div class="fact-label">Raw date-span check</div><div class="fact-value"><strong>25 elapsed days</strong> from Dec. 14 to Jan. 8. Because this does not equal the 24-night charge, use the university's published $360 full-break fee rather than deriving the bill from the endpoints.</div></div>
    </div>
    <p><a href="https://housing.dasa.ncsu.edu/assignments/break-and-transition-housing/" target="_blank" rel="noopener noreferrer">NC State Break and Transition Housing</a></p>

    <h3>2026–27 timing references</h3>
    <div class="facts">
      <div class="fact"><div class="fact-label">Fall 2026 final exams end</div><div class="fact-value"><strong>Dec. 9, 2026</strong></div></div>
      <div class="fact"><div class="fact-label">Spring 2027 housing check-in</div><div class="fact-value"><strong>Jan. 7–10, 2027</strong></div></div>
      <div class="fact"><div class="fact-label">Spring 2027 classes begin</div><div class="fact-value"><strong>Jan. 11, 2027</strong></div></div>
      <div class="fact"><div class="fact-label">University-closed winter holiday</div><div class="fact-value"><strong>Dec. 24, 2026–Jan. 1, 2027 = 9 calendar days inclusive</strong>. This is the university closure period, not the full housing intersession.</div></div>
    </div>
    <div class="use-note"><strong>2026–27 caution:</strong> As of Sept. 15, 2026, University Housing has posted the $15/night winter-break rate and the 2026–27 housing agreement, but its Break and Transition Housing page still shows the exact 2025–26 winter-break dates and $360 flat charge. Do not present $360 as the confirmed 2026–27 full-break total until Housing posts the new dates/charge.</div>
    <p><a href="https://studentservices.ncsu.edu/calendars/academic-calendar/" target="_blank" rel="noopener noreferrer">NC State Academic Calendar</a> · <a href="https://housing.dasa.ncsu.edu/assignments/move-in-information/" target="_blank" rel="noopener noreferrer">Spring 2027 Housing Move-In</a> · <a href="https://housing.dasa.ncsu.edu/residential-communities/costs/" target="_blank" rel="noopener noreferrer">University Housing Costs</a></p>
  `);
})();
