document.addEventListener("DOMContentLoaded", function() {
  document.querySelectorAll('[id^="configuration-"]').forEach(function(ruleModal) {
    const hasError = ruleModal.querySelector(".errorlist");
    if (hasError) {
      const ruleId = ruleModal.id.replace("configuration-", "");
      const ruleTableRow = document.getElementById(`execution_order-${ruleId}`);

      if (ruleTableRow) {
        ruleTableRow.parentNode.classList.add("error-border");
      }
    }
  });
});
