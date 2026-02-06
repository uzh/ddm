function hideOrShowConsentLabels() {
    const consentEnabled = document.getElementById("id_briefing_consent_enabled");
    const labelYes = document.getElementById("id_briefing_consent_label_yes");
    const labelNo = document.getElementById("id_briefing_consent_label_no");

    if (consentEnabled && consentEnabled.checked) {
        if (labelYes && labelYes.parentElement) {
            labelYes.parentElement.style.display = '';
        }
        if (labelNo && labelNo.parentElement) {
            labelNo.parentElement.style.display = '';
        }
    } else {
        if (labelYes && labelYes.parentElement) {
            labelYes.parentElement.style.display = 'none';
        }
        if (labelNo && labelNo.parentElement) {
            labelNo.parentElement.style.display = 'none';
        }
    }
}

document.addEventListener('DOMContentLoaded', function() {
    hideOrShowConsentLabels();

    const consentEnabled = document.getElementById("id_briefing_consent_enabled");
    if (consentEnabled) {
        consentEnabled.addEventListener('change', hideOrShowConsentLabels);
    }
});