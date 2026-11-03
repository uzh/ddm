(function () {
  const stepSelect = document.getElementById('test-nav-step');
  const pageSelect = document.getElementById('test-nav-page');

  function syncPageVisibility() {
    const isQuestionnaire = stepSelect.value === 'questionnaire';
    pageSelect.classList.toggle('d-none', !isQuestionnaire);
    pageSelect.disabled = !isQuestionnaire;
  }
  stepSelect.addEventListener('change', syncPageVisibility);
  syncPageVisibility();
})();
