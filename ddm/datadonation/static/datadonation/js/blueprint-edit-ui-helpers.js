/**
 * Updates rule description in the form of a proper sentence.
 */
updateRuleDescription = function( id ) {
  const id_prefix = "id_processingrule_set-" + id + "-";
  const field = $("[id^=" + id_prefix + "field]").val();
  const operator = $("[id^=" + id_prefix + "comparison_operator]").val();
  const comp_value = $("[id^=" + id_prefix + "comparison_value]").val();
  const repl_value = $("[id^=" + id_prefix + "replacement_value]").val();

  let msg = "";
  if ( field !== "" ) {
    if ( operator === "" && field !== "" ){
      msg = "Keep field '" + field + "' in uploaded data.";
    } else if ( operator === "regex-delete-match" ) {
      msg = "Delete parts of '" + field + "' field that match the following regex expression: '" + comp_value + "'.";
    } else if ( operator === "regex-replace-match" ) {
      msg = "Replace parts of '" + field + "' field that match the regex expression '" + comp_value + "' with '" + repl_value + "'.";
    } else if ( operator === "regex-delete-row" ) {
      msg = "Delete entry if '" + field + "' field value matches the following regex expression: '" + comp_value + "'.";
    } else {
      msg = "Delete row if current value of field '" + field + "' " + operator + " '" + comp_value + "'.";
    }
    $("[id=step-description-" + id + "]").html(msg);
  }
};


/**
 * Updates the field value placeholders in the filter settings overview.
 */
updateFieldValue = function( id ) {
  $("#configuration-" + id).find("input").each(function() {
    if (!$(this).is("button")) {
      let fieldName = $(this).attr("id").split("-").pop();
      let targetId = "#" + fieldName + "-" + id;
      $( targetId ).html($(this).val());
    }
  });
};

hideErrorMessages = function(id) {
  const independentFields = ["execution_order", "name", "field"];
  for (let i = 0; i < independentFields.length; i++) {
    let curElement = $("#id_processingrule_set-" + id + "-" + independentFields[i]);
    curElement.siblings( ".form-error" ).hide();
  }
}

checkNoFieldsMissing = function( id ) {
  const independentFields = ["execution_order", "name", "field"];

  for (let i = 0; i < independentFields.length; i++) {
    let val = $("[id$=" + id + "-" + independentFields[i] + "]").val();

    if (val === "") {
      let curElement = $("#id_processingrule_set-" + id + "-" + independentFields[i]);
      curElement.siblings( ".form-error" ).show();
      return(false);
    }
  }

  let comparisonOperator = $("#id_processingrule_set-" + id + "-comparison_operator");
  if (comparisonOperator.val() !== "") {
    let comparisonValue = $("#id_processingrule_set-" + id + "-comparison_value").val();
    if (comparisonValue === "") {
      let curElement = $("#id_processingrule_set-" + id + "-comparison_value");
      curElement.siblings( ".form-error" ).show();
      return(false);
    }
  }
  return(true);
}

closeModal = function(id) {
  let modal = $("#configuration-" + id);
  modal.hide();
  $("body").removeClass("modal-open").removeAttr("style");
  $(".modal-backdrop").remove();
}

/**
 * On OK-click in modal, update filter settings overview.
 */
$( "body" ).on("click", "button[class*='ddm-modal-ok']", function() {
  const current_id = $(this).attr("id").match(/\d+/)[0];
  hideErrorMessages(current_id);
  if (checkNoFieldsMissing(current_id)) {
    updateRuleDescription(current_id);
    updateFieldValue(current_id);
    closeModal(current_id);
  }
});

$( "body" ).on("click", "button[class*='ddm-modal-cancel']", function() {
  const current_id = $(this).attr("id").match(/\d+/)[0];
  let e = $("#execution_order-" + current_id);

  if ($.trim(e.text()) === 'None') {
    $("#configuration-" + current_id).remove();
    $('#inlineform-table tr:last').remove();

    let totalFormElement = $("#id_processingrule_set-TOTAL_FORMS");
    let currentFormN = totalFormElement.val();
    totalFormElement.val(parseInt(currentFormN) - 1);
  }
  closeModal(current_id);
});


$(document).ready(function() {
  let IDs = new Set();
  $("[id^=id_processingrule_set-]").each(function() {
    if( /\d+/.test($( this ).attr("id")) ) {
      IDs.add($( this ).attr("id").match(/\d+/)[0]);
    }
  });
  for ( const id of IDs ) {
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
  newModal.find( ".ddm-admin-form" ).replaceWith($("#empty-form").html().replace(/__prefix__/g, formIdx));
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
