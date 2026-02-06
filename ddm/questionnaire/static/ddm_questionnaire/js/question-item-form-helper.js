/**
 * Helper function to add new question item formsets.
 */
document.getElementById('add-question-item-form').addEventListener('click', function() {
  const container = document.getElementById('question-item-form-container');
  const emptyForm = document.getElementById('empty-question-item-form').innerHTML;
  const totalForms = document.getElementById('id_questionitem_set-TOTAL_FORMS');
  const formCount = parseInt(totalForms.value);

  // Replace __prefix__ with the actual form index
  const newForm = emptyForm.replace(/__prefix__/g, formCount);

  // Create temporary container to manipulate innerHtml
  const template = document.createElement('template');
  template.innerHTML = newForm;
  const row = template.content.firstElementChild;

  // Guess form values and prefill
  const indexSelector = '[id^="id_questionitem_set-"][id$="-index"]'
  const indexInput = row.querySelector(indexSelector);

  if (indexInput) {
    indexInput.value = getMaxValue(indexSelector) + 1;
  }

  const valueSelector = '[id^="id_questionitem_set-"][id$="-value"]'
  const valueInput = row.querySelector(valueSelector);
  if (valueInput) {
    valueInput.value = getMaxValue(valueSelector) + 1;
  }

  // Remove no elements placeholder
  document.getElementById('no-question-items-placeholder')?.remove();

  container.appendChild(row);
  totalForms.value = formCount + 1;
});

function getMaxValue(selector) {
  const values = Array.from(document.querySelectorAll(selector))
      .map(el => parseInt(el.value, 10) );
  values.push(0)
  return Math.max(...values.filter(Number.isFinite));
}

/**
 * Helper function to show/hide question item section for "Open Question" type questions.
 */
function hideOrShowQuestionItems() {
  const showQuestionItems = document.getElementById('id_multi_item_response').checked;
  const questionItemTable = document.getElementById('question-item-table');
  if (showQuestionItems) {
    questionItemTable.classList.remove('d-none')
  } else {
    questionItemTable.classList.add('d-none');
  }
}

document.getElementById("id_multi_item_response")?.addEventListener("change", function () {
  hideOrShowQuestionItems();
});

document.addEventListener("DOMContentLoaded", function() {
  if (document.getElementById("id_multi_item_response")) {
    hideOrShowQuestionItems();
  }
});
