function hideOrShowConsentLabels() {
  const consentEnabled = document.getElementById("id_briefing_consent_enabled");
  const labelContainer = document.getElementById("consentLabelContainer");

  if (consentEnabled && consentEnabled.checked) {
    if (labelContainer) {
      labelContainer.style.opacity = "1";
      labelContainer.style.visibility = "visible";
      labelContainer.style.maxHeight = "500px";
    }
  } else {
    if (labelContainer) {
      labelContainer.style.opacity = "0";
      labelContainer.style.visibility = "hidden";
      labelContainer.style.maxHeight = "0";
    }
  }
}

document.addEventListener('DOMContentLoaded', function() {
  hideOrShowConsentLabels();

  const consentEnabled = document.getElementById("id_briefing_consent_enabled");
  if (consentEnabled) {
    consentEnabled.addEventListener('change', hideOrShowConsentLabels);
  }

  const labelContainer = document.getElementById("consentLabelContainer");
  if (labelContainer) {
    labelContainer.style.transition = "opacity 0.5s ease, visibility 0.5s ease, max-height 0.5s ease";
  }
});