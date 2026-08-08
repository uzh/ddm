function showConditionalSettings() {
  const inputType = document.getElementById("id_input_type").value;

  const numberSettingsContainer = document.getElementById("number-value-settings");
  const stringSettingsContainer = document.getElementById("input-length-settings");
  if (inputType === "numbers") {
    numberSettingsContainer.style.display = "flex";
    stringSettingsContainer.style.display = "none";
  } else {
    numberSettingsContainer.style.display = "none";
    stringSettingsContainer.style.display = "flex";
  }
}

document.addEventListener("DOMContentLoaded", function() {
  showConditionalSettings();
  document.getElementById("id_input_type").addEventListener("change", showConditionalSettings);
});
