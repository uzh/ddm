hideOrShowReplacementValue = function( id ) {
  let replacementInput = $("#id_processingrule_set-" + id + "-replacement_value");
  let val = $("[id$=" + id + "-comparison_operator]").val();

  // if value contains "replace match"
  if (val.indexOf("regex-replace-match") >= 0 ) {
    replacementInput.show();
    replacementInput.siblings().show();
  } else {
    replacementInput.hide();
    replacementInput.siblings().hide();
  }
}

/**
 * On OK-click in modal, update filter settings overview.
 */
$( "body" ).on("change", "select[id$='-comparison_operator']", function() {
  const current_id = $(this).attr("id").match(/\d/)[0];
  hideOrShowReplacementValue(current_id);

});

$(document).ready(function() {
  let IDs = new Set();
  $("[id$=-comparison_operator]").each(function() {
    if( /\d/.test($( this ).attr("id")) ) {
      IDs.add($( this ).attr("id").match(/\d/)[0]);
    }
  });
  for ( const id of IDs ) {
    hideOrShowReplacementValue(id);
  }
});
