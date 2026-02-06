/**
 * Helper function to add new scale point formsets.
 */
document.getElementById('add-scale-point-form').addEventListener('click', function() {
  const container = document.getElementById('scale-point-form-container');
  const emptyForm = document.getElementById('empty-scale-point-form').innerHTML;
  const totalForms = document.getElementById('id_scalepoint_set-TOTAL_FORMS');
  const formCount = parseInt(totalForms.value);

  // Replace __prefix__ with the actual form index
  const newForm = emptyForm.replace(/__prefix__/g, formCount);

  // Create temporary container to manipulate innerHtml
  const template = document.createElement('template');
  template.innerHTML = newForm;
  const row = template.content.firstElementChild;

  // Guess form values and prefill
  const indexSelector = '[id^="id_scalepoint_set-"][id$="-index"]'
  const indexInput = row.querySelector(indexSelector);

  if (indexInput) {
    indexInput.value = getMaxValue(indexSelector) + 1;
  }

  const valueSelector = '[id^="id_scalepoint_set-"][id$="-value"]'
  const valueInput = row.querySelector(valueSelector);
  if (valueInput) {
    valueInput.value = getMaxValue(valueSelector) + 1;
  }

  // Remove no elements placeholder
  document.getElementById('no-scales-placeholder')?.remove();

  container.appendChild(row);
  totalForms.value = formCount + 1;
});

function getMaxValue(selector) {
  const values = Array.from(document.querySelectorAll(selector))
      .map(el => parseInt(el.value, 10) );
  values.push(0)
  return Math.max(...values.filter(Number.isFinite));
}
