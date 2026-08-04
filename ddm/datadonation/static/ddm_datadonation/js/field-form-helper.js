// TODO: Combine with equivalent file-path-form-helper.js
document.getElementById("add-field-form").addEventListener("click", function() {
    const container = document.getElementById("field-table-body");
    const emptyForm = document.getElementById("empty-field-form").innerHTML;
    const emptyPlaceholder = document.getElementById("no-field-table-row");
    const totalForms = document.getElementById("id_extractionfield_set-TOTAL_FORMS");
    const formCount = parseInt(totalForms.value);

    // Replace __prefix__ with the actual form index
    const newForm = emptyForm.replace(/__prefix__/g, formCount);

    container.insertAdjacentHTML("beforeend", newForm);
    emptyPlaceholder?.remove();

    totalForms.value = formCount + 1;
});
