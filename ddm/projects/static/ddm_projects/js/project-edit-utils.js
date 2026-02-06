function hideOrShowParameter() {
    const urlParameterEnabled = document.getElementById("id_url_parameter_enabled");
    const expectedUrlParameters = document.getElementById("id_expected_url_parameters");

    if (urlParameterEnabled && urlParameterEnabled.checked) {
        if (expectedUrlParameters && expectedUrlParameters.parentElement) {
            expectedUrlParameters.parentElement.style.display = '';
        }
    } else {
        if (expectedUrlParameters && expectedUrlParameters.parentElement) {
            expectedUrlParameters.parentElement.style.display = 'none';
        }
    }
}

function hideOrShowRedirect() {
    const redirectEnabled = document.getElementById("id_redirect_enabled");
    const redirectTarget = document.getElementById("id_redirect_target");

    if (redirectEnabled && redirectEnabled.checked) {
        if (redirectTarget && redirectTarget.parentElement) {
            redirectTarget.parentElement.style.display = '';
        }
    } else {
        if (redirectTarget && redirectTarget.parentElement) {
            redirectTarget.parentElement.style.display = 'none';
        }
    }
}

document.addEventListener('DOMContentLoaded', function() {
    hideOrShowParameter();
    hideOrShowRedirect();

    const urlParameterEnabled = document.getElementById("id_url_parameter_enabled");
    if (urlParameterEnabled) {
        urlParameterEnabled.addEventListener('change', hideOrShowParameter);
    }

    const redirectEnabled = document.getElementById("id_redirect_enabled");
    if (redirectEnabled) {
        redirectEnabled.addEventListener('change', hideOrShowRedirect);
    }

    const accordionButtons = document.querySelectorAll('.ddm-accordion-btn');
    accordionButtons.forEach(function(button) {
        button.addEventListener('click', function() {
            if (this.getAttribute('aria-expanded') === 'true') {
                this.classList.add('sign-accordion-open');
            } else {
                this.classList.remove('sign-accordion-open');
            }
        });
    });
});
