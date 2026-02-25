function hideOrShowZipConfig() {
  const expFileFormat = document.getElementById("id_upload_type").value;

  const zipSettingsDiv = document.getElementById("file-uploader-zip-settings");

  if (expFileFormat === "zip file") {
    zipSettingsDiv.style.margin = "";
    zipSettingsDiv.style.padding = "";
    zipSettingsDiv.style.opacity = "1";
    zipSettingsDiv.style.visibility = "visible";
    zipSettingsDiv.style.maxHeight = "500px";
  } else {
    zipSettingsDiv.style.opacity = "0";
    zipSettingsDiv.style.visibility = "hidden";
    zipSettingsDiv.style.maxHeight = "0";
    zipSettingsDiv.style.margin = "0";
    zipSettingsDiv.style.padding = "0";
  }
}

document.addEventListener("DOMContentLoaded", function() {
  const zipSettingsDiv = document.getElementById("file-uploader-zip-settings");
  if (zipSettingsDiv) {
    zipSettingsDiv.style.transition = "opacity 0.3s ease, visibility 0.3s ease, max-height 0.5s ease";
  }

  hideOrShowZipConfig();

  document.getElementById("id_upload_type").addEventListener("change", function() {
    hideOrShowZipConfig();
  });

});
