hideOrShowReplacementAndComparisonValue = function (id) {
  let replacementInput = $("#id_processingrule_set-" + id + "-replacement_value");
  let comparisonValue = $("#id_processingrule_set-" + id + "-comparison_value");

  let val = $("[id$=" + id + "-comparison_operator]").val();

  if (val.indexOf("regex-replace-match") >= 0) {
    replacementInput.parent().show();
    comparisonValue.parent().show();
  } else if (val === "") {
    replacementInput.parent().hide();
    comparisonValue.parent().hide();
  } else {
    replacementInput.parent().hide();
    comparisonValue.parent().show();
  }

  if (val.indexOf("regex") >= 0) {
    $('label[for="id_processingrule_set-' + id + '-comparison_value"]').text("Regular expression (regex):");
  } else {
    $('label[for="id_processingrule_set-' + id + '-comparison_value"]').text("Comparison value:");
  }
}

$("body").on("change", "select[id$='-comparison_operator']", function () {
  const current_id = $(this).attr("id").match(/\d+/)[0];
  hideOrShowReplacementAndComparisonValue(current_id);
});

$(document).ready(function () {
  let IDs = new Set();
  $("[id$=-comparison_operator]").each(function () {
    if (/\d+/.test($(this).attr("id"))) {
      IDs.add($(this).attr("id").match(/\d+/)[0]);
    }
  });
  for (const id of IDs) {
    hideOrShowReplacementAndComparisonValue(id);
  }
});
