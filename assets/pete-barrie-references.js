(function(){
  const housingCard=document.getElementById('ncsu-housing-rates-2026-27');
  if(housingCard && !housingCard.querySelector('.pete-fraccaroli-evidence')){
    const body=housingCard.querySelector('.ref-body');
    if(body){
      body.insertAdjacentHTML('beforeend', `
        <hr class="rule">
        <h2>Pete Fraccaroli — title verification</h2>
        <div class="pete-fraccaroli-evidence">
          <div class="facts">
            <div class="fact"><div class="fact-label">University Housing title</div><div class="fact-value"><strong>Director, Facilities and Business Operations</strong></div></div>
          </div>
          <div class="use-note"><strong>Reporting note:</strong> NC State's University Housing staff directory lists Pete Fraccaroli as Director of Facilities and Business Operations. NC State DASA News also identifies him as University Housing's director of facilities and business operations.</div>
          <p><a href="https://housing.dasa.ncsu.edu/staff/pdfracca/" target="_blank" rel="noopener noreferrer">NC State University Housing — Pete Fraccaroli staff profile</a> · <a href="https://news.dasa.ncsu.edu/university-housing-expands-campus-living-options-with-university-towers-acquisition-renovation/" target="_blank" rel="noopener noreferrer">NC State DASA News — University Towers acquisition</a></p>
        </div>
      `);
    }
  }

  const rentTrendCard=document.getElementById('raleigh-rent-trend');
  if(rentTrendCard && !rentTrendCard.querySelector('.thomas-barrie-evidence')){
    const body=rentTrendCard.querySelector('.ref-body');
    if(body){
      body.insertAdjacentHTML('beforeend', `
        <hr class="rule">
        <h2>Thomas Barrie — title and housing expertise</h2>
        <div class="thomas-barrie-evidence">
          <div class="facts">
            <div class="fact"><div class="fact-label">College of Design title</div><div class="fact-value"><strong>Emeritus Professor of Architecture</strong></div></div>
            <div class="fact"><div class="fact-label">Housing role</div><div class="fact-value"><strong>Director, Affordable Housing and Sustainable Communities Initiative</strong></div></div>
            <div class="fact"><div class="fact-label">Additional role</div><div class="fact-value"><strong>Coordinator, Master of Advanced Architectural Studies</strong></div></div>
          </div>
          <div class="use-note"><strong>Reporting note:</strong> NC State's College of Design profile lists Barrie's current titles and says he founded the Affordable Housing and Sustainable Communities Initiative in 2007. The profile describes him as a recognized housing expert and advocate in the Triangle.</div>
          <p><a href="https://design.ncsu.edu/people/tmbarrie/" target="_blank" rel="noopener noreferrer">NC State College of Design — Thomas Barrie profile</a></p>
        </div>
      `);
    }
  }
})();
