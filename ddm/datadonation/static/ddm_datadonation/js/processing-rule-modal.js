hideOrShowReplacementAndComparisonValue = function (id) {
    const inputId = "id_processingrule_set-".concat(String(id)).concat("-replacement_value");
    const comparisonId = "id_processingrule_set-".concat(String(id)).concat("-comparison_value");
    const replacementInput = document.getElementById(inputId);
    const comparisonValue = document.getElementById(comparisonId);
    const comparisonOperator = document.querySelector(`[id$='${id}-comparison_operator']`).value;

    if (comparisonOperator.indexOf("regex-replace-match") >= 0) {
        replacementInput.parentElement.classList.remove("d-none");
        comparisonValue.parentElement.classList.remove("d-none");
        replacementInput.parentElement.style.display = "block";
        comparisonValue.parentElement.style.display = "block";
    } else if (comparisonOperator === "") {
        replacementInput.parentElement.style.display = "none";
        comparisonValue.parentElement.style.display = "none";
    } else {
        replacementInput.parentElement.style.display = "none";
        comparisonValue.parentElement.classList.remove("d-none");
        comparisonValue.parentElement.style.display = "block";
    }

    const comparisonLabel = document.querySelector('label[for="id_processingrule_set-' + id + '-comparison_value"]');

    if (comparisonOperator.indexOf("regex") >= 0) {
        comparisonLabel.textContent = "Regular expression (regex):";
    } else {
        comparisonLabel.textContent = "Comparison value:";
    }
}

document.body.addEventListener("change", function (event) {
    if (event.target.matches("select[id$='-comparison_operator']")) {
        const currentId = event.target.id.match(/\d+/)[0];
        hideOrShowReplacementAndComparisonValue(currentId);
    }
});

document.addEventListener("DOMContentLoaded", function () {
    let IDs = new Set();
    document.querySelectorAll("[id$='-comparison_operator']").forEach(function (element) {
        const match = element.id.match(/\d+/);
        if (match) {
            IDs.add(match[0]);
        }
    });

    IDs.forEach(function (id) {
        hideOrShowReplacementAndComparisonValue(id);
    });
});
