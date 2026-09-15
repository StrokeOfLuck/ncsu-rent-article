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
    <div class="use-note"><strong>Reporting note:</strong> This is a separate published charge for students who use winter-break housing. Do not add it automatically to every resident's academic-year cost. It matters when comparing the standard university housing period with a continuous off-campus lease.</div>
    <p><a href="https://housing.dasa.ncsu.edu/residential-communities/costs/" target="_blank" rel="noopener noreferrer">NC State University Housing costs</a></p>
  `);
})();
