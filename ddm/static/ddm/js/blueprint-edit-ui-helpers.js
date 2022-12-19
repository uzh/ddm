/**
 * Updates rule description in the form of a proper sentence.
 */
updateRuleDescription = function( id ) {
  const id_prefix = "id_processingrule_set-" + id + "-";
  const field = $("[id^=" + id_prefix + "field]").val();
  const operator = $("[id^=" + id_prefix + "comparison_operator]").val();
  const comp_value = $("[id^=" + id_prefix + "comparison_value]").val();

  let msg = "";
  if ( field !== "" ) {
    if ( operator === "" && field !== "" ){
      msg = "Keep field '" + field + "' in uploaded data.";
    } else if ( operator === "regex" ) {
      msg = "Delete parts of " + field + "-value that match the following regex expression: " + comp_value + ".";
    } else {
      msg = "Delete row if current value of field '" + field + "' " + operator + " " + comp_value + ".";
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


/**
 * On OK-click in modal, update filter settings overview.
 */
$( "body" ).on("click", "button[class*='ddm-modal-ok']", function() {
  const current_id = $(this).attr("id").match(/\d/)[0];
  updateRuleDescription(current_id);
  updateFieldValue(current_id);
});


$(document).ready(function() {
  let IDs = new Set();
  $("[id^=id_processingrule_set-]").each(function() {
    if( /\d/.test($( this ).attr("id")) ) {
      IDs.add($( this ).attr("id").match(/\d/)[0]);
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
    if( /\d/.test($(this).attr("id"))) {
      IDs.push($(this).attr("id").match(/\d/)[0]);
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
