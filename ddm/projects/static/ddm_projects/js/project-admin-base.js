document.addEventListener('DOMContentLoaded', function () {
    var checkboxes = document.querySelectorAll('input[type="checkbox"]');
    checkboxes.forEach(function (checkbox) {
        // Create a new label element
        var lbl = document.createElement('label');
        lbl.setAttribute('for', checkbox.id);
        lbl.classList.add('checkmark');

        // Insert the label immediately after the checkbox
        if (checkbox.nextSibling) {
            checkbox.parentNode.insertBefore(lbl, checkbox.nextSibling);
        } else {
            checkbox.parentNode.appendChild(lbl);
        }
    });
});
