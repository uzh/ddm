document.getElementById("add-file-path-form").addEventListener("click", function() {
    const container = document.getElementById("file-path-formset-container");
    const emptyForm = document.getElementById("empty-file-path-form").innerHTML;
    const totalForms = document.getElementById("id_blueprintfilepath_set-TOTAL_FORMS");
    const formCount = parseInt(totalForms.value);

    // Replace __prefix__ with the actual form index
    const newForm = emptyForm.replace(/__prefix__/g, formCount);

    container.insertAdjacentHTML("beforeend", newForm);
    totalForms.value = formCount + 1;
});
