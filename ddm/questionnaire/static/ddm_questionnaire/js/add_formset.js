document.addEventListener("DOMContentLoaded", function () {
    const formsetTable = document.getElementById("formset-table").querySelector("tbody");
    const addButton = document.getElementById("add-form");
    const totalForms = document.querySelector("[name$='-TOTAL_FORMS']");

    if (!totalForms) return;

    // Extract the formset prefix dynamically
    const formsetPrefix = totalForms.name.replace("-TOTAL_FORMS", "");

    addButton.addEventListener("click", function () {
        const formCount = parseInt(totalForms.value);
        const lastRow = formsetTable.querySelector("tr:last-of-type");

        if (!lastRow) return;

        // Clone the last row
        const newRow = lastRow.cloneNode(true);

        // Update form field names, IDs, and clear values
        newRow.innerHTML = newRow.innerHTML.replace(
            new RegExp(`${formsetPrefix}-(\\d+)-`, "g"),
            `${formsetPrefix}-${formCount}-`
        );

        // Find the maximum existing index
        let maxIndex = 0;
        document.querySelectorAll(`[name^="${formsetPrefix}-"][name$="-index"]`).forEach(input => {
            const value = parseInt(input.value, 10);
            if (!isNaN(value) && value > maxIndex) {
                maxIndex = value;
            }
        });

        // Clear input values but retain hidden fields like `question`
        newRow.querySelectorAll("input").forEach(input => {
            if (!input.name.endsWith("target_question") && !input.name.endsWith("target_item")) {
                if (input.type === "checkbox") {
                    input.checked = false;
                } else if (input.name.endsWith("-index")) {
                    input.value = maxIndex + 1;
                } else if (input.type === "hidden" && input.name.includes("-id")) {
                    input.value = "";
                } else {
                    input.value = "";
                }
            }
        });

        // Clear select values
        newRow.querySelectorAll("select").forEach(input => {
            if (input.name.endsWith("condition_operator")) {
                input.value = "";
            } else if (input.name.endsWith("source")) {
                input.value = "";
            } else if (input.name.endsWith("combinator")) {
                input.value = "";
            }
        });

        // Append new row to the table
        formsetTable.appendChild(newRow);

        // Update TOTAL_FORMS value
        totalForms.value = formCount + 1;
    });
});
