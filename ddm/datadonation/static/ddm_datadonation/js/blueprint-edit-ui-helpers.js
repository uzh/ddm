/**
 * Include rule description in the form of a proper sentence in the extraction rules table.
 */
function updateRuleDescription(id) {
  const id_prefix = "id_processingrule_set-" + id + "-";
  const field = document.querySelector(`[id^="${id_prefix}field"]`)?.value;
  const operator = document.querySelector(`[id^="${id_prefix}comparison_operator"]`)?.value;
  const comp_value = document.querySelector(`[id^="${id_prefix}comparison_value"]`)?.value;
  const repl_value = document.querySelector(`[id^="${id_prefix}replacement_value"]`)?.value;

  let msg = "";
  if (field !== "") {
    if (operator === "" && field !== "") {
      msg = "Keep field '" + field + "' in uploaded data.";
    } else if (operator === "regex-delete-match") {
      msg = "Delete parts of '" + field + "' field that match the following regex expression: '" + comp_value + "'.";
    } else if (operator === "regex-replace-match") {
      msg = "Replace parts of '" + field + "' field that match the regex expression '" + comp_value + "' with '" + repl_value + "'.";
    } else if (operator === "regex-delete-row") {
      msg = "Delete entry if '" + field + "' field value matches the following regex expression: '" + comp_value + "'.";
    } else {
      msg = "Delete row if current value of field '" + field + "' " + operator + " '" + comp_value + "'.";
    }

    const descriptionElement = document.querySelector(`[id=step-description-${id}]`);
    if (descriptionElement) {
      descriptionElement.textContent = msg;
    }
  }

}

/**
 * Updates the field value placeholders in the extraction rules table.
 */
function updateRuleTable(id) {
  let container = document.getElementById("configuration-" + id);
  let inputs = container.querySelectorAll("input");

  inputs.forEach(function(input) {
    if (input.type !== "button") {
      let fieldName = input.id.split("-").pop();
      let targetId = fieldName + "-" + id;
      let targetElement = document.getElementById(targetId);

      if (targetElement) {
        targetElement.textContent = input.value;
      }
    }
  });

  updateRuleDescription(id);
}

function hideErrorMessages(id) {
  const independentFields = ["execution_order", "name", "field"];
  for (let i = 0; i < independentFields.length; i++) {
    const curElement = document.getElementById(`id_processingrule_set-${id}-${independentFields[i]}`);
    if (curElement) {
      const errorElements = curElement.parentElement.querySelectorAll(".form-error");
      errorElements.forEach(function(errorElement) {
        errorElement.style.display = "none";
      });
    }
  }
}

function checkNoFieldsMissing(id) {
  const independentFields = ["execution_order", "name", "field"];

  for (let i = 0; i < independentFields.length; i++) {
    const fieldElement = document.querySelector(`[id$="${id}-${independentFields[i]}"]`);
    const val = fieldElement ? fieldElement.value : "";

    if (val === "") {
      const curElement = document.getElementById(`id_processingrule_set-${id}-${independentFields[i]}`);
      if (curElement) {
        const errorElements = curElement.parentElement.querySelectorAll(".form-error");
        errorElements.forEach(function (errorElement) {
          errorElement.style.display = "block";
        });
      }
      return false;
    }
  }

  const comparisonOperator = document.getElementById(`id_processingrule_set-${id}-comparison_operator`);
  if (comparisonOperator && comparisonOperator.value !== "") {
    const comparisonValue = document.getElementById(`id_processingrule_set-${id}-comparison_value`);
    if (comparisonValue && comparisonValue.value === "") {
      const errorElements = comparisonValue.parentElement.querySelectorAll(".form-error");
      errorElements.forEach(function (errorElement) {
        errorElement.style.display = "block";
      });
      return false;
    }
  }

  return true;
}

function closeModal(id) {
  const modal = document.getElementById(`configuration-${id}`);
  if (modal) {
    modal.style.display = "none";
  }

  const body = document.body;
  body.classList.remove("modal-open");
  body.removeAttribute("style");

  const modalBackdrop = document.querySelectorAll(".modal-backdrop");
  modalBackdrop.forEach(function (backdrop) {
    backdrop.remove();
  });
}

/**
 * On OK-click in modal, update filter settings overview.
 */
document.body.addEventListener("click", function (event) {
  if (event.target.tagName === "BUTTON" && event.target.className.includes("ddm-modal-ok")) {
    const current_id = event.target.id.match(/\d+/)[0];
    hideErrorMessages(current_id);
    if (checkNoFieldsMissing(current_id)) {
      updateRuleTable(current_id);
      closeModal(current_id);
    }
  }
});


document.body.addEventListener("click", function (event) {
  if (event.target.tagName === "BUTTON" && event.target.className.includes("ddm-modal-cancel")) {
    const current_id = event.target.id.match(/\d+/)[0];
    const e = document.getElementById(`execution_order-${current_id}`);

    if (e && e.textContent.trim() === "None") {
      const configurationElement = document.getElementById(`configuration-${current_id}`);
      if (configurationElement) {
        configurationElement.remove();
      }

      const lastRow = document.querySelector("#inlineform-table tr:last-child");
      if (lastRow) {
        lastRow.remove();
      }

      const totalFormElement = document.getElementById("id_processingrule_set-TOTAL_FORMS");
      if (totalFormElement) {
        const currentFormN = parseInt(totalFormElement.value, 10);
        totalFormElement.value = currentFormN - 1;
      }
    }
    closeModal(current_id);
  }
});


document.addEventListener("DOMContentLoaded", function () {
  const IDs = new Set();
  const elements = document.querySelectorAll("[id^=id_processingrule_set-]");

  elements.forEach(function (element) {
    const idMatch = element.id.match(/\d+/);
    if (idMatch) {
      IDs.add(idMatch[0]);
    }
  });

  for (const id of IDs) {
    updateRuleDescription(id);
  }
});


/**
 * Handles the addition of additional inline forms.
 */
$("#add-inline-form").on("click", function() {
  let IDs = [];
  $("[id^=id_processingrule_set-]").each(function() {
    if( /\d+/.test($(this).attr("id"))) {
      IDs.push($(this).attr("id").match(/\d+/)[0]);
    }
  });
  let formIdx;
  if ( !IDs.length ) {
    formIdx = 0;
  } else {
    formIdx = Math.max(...IDs) + 1;
  }

  // Add new modal.
  let newModal = $("[id^=configuration-]").first().clone();
  newModal.attr("id", "configuration-" + formIdx );
  newModal.find( ".rule-configuration-form" ).replaceWith($("#empty-form").html().replace(/__prefix__/g, formIdx));
  newModal.find( "button" ).attr("id", "ddm-modal-ok-" + formIdx );
  newModal.find("input[id*='execution_order']").val(formIdx + 1);
  $("[id^=configuration-]").last().after(newModal);

  // Add new form placeholder.
  let newPlaceholder = $("#empty-form-placeholder").find("tbody:first");

  $("#inlineform-table > tbody:last-child").append(newPlaceholder.html().replace(/__prefix__/g, formIdx));

  // Update management form.
  $("#id_processingrule_set-TOTAL_FORMS").val(parseInt(formIdx) + 1);

  // Open modal.
  newModal.modal("toggle");
});
