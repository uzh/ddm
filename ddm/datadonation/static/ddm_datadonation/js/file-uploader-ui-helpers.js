function hideOrShowZipConfig() {
  const expFileFormat = document.getElementById("id_upload_type").value;

  const zipSettingsDiv = document.getElementById("file-uploader-zip-settings");

  if (expFileFormat === "zip file") {
    zipSettingsDiv.style.display = "";
  } else {
    zipSettingsDiv.style.display = "none";
  }
}

document.addEventListener("DOMContentLoaded", function() {
  hideOrShowZipConfig();

  document.getElementById("id_upload_type").addEventListener("change", function() {
    hideOrShowZipConfig();
  });

});
