// Get variables from template.
const file_uploader_meta = JSON.parse(document.getElementById("file_uploader_meta").textContent);

function hideOrShowCsvDelimiter() {
  const expFileFormat = document.getElementById("id_exp_file_format").value;
  const csvDelimiterParent = document.getElementById("id_csv_delimiter").parentNode;

  if (expFileFormat === "csv") {
    // Show the parent element
    csvDelimiterParent.style.display = "";
  } else {
    // Hide the parent element
    csvDelimiterParent.style.display = "none";
  }
}

function hideOrShowFilePath() {
  const fileUploaderVal = document.getElementById("id_file_uploader").value;

  const fileIdentificationId = "IdentificationSettings";
  const fileIdentificationButton = document.getElementById(`accordionButton${fileIdentificationId}`);
  const fileIdentificationBody = document.getElementById(`collapse${fileIdentificationId}`);

  if (file_uploader_meta[fileUploaderVal] === "single file") {
    fileIdentificationButton.disabled = true;

    fileIdentificationButton.classList.add("collapsed");
    fileIdentificationBody.classList.remove("show");

  } else {
    fileIdentificationButton.disabled = false;
  }
}

function hideOrShowJsonRoot() {
  const expFileFormat = document.getElementById("id_exp_file_format").value;

  const jsonExtractionRootParent = document.getElementById("id_json_extraction_root");

  if (jsonExtractionRootParent) {
    if (expFileFormat === "json") {
      jsonExtractionRootParent.parentNode.style.display = "";
    } else {
      jsonExtractionRootParent.parentNode.style.display = "none";
    }
  }
}

document.addEventListener("DOMContentLoaded", function() {
  hideOrShowCsvDelimiter();
  hideOrShowFilePath();
  hideOrShowJsonRoot();

  document.getElementById("id_exp_file_format").addEventListener("change", function() {
    hideOrShowCsvDelimiter();
    hideOrShowJsonRoot();
  });

  document.getElementById("id_file_uploader").addEventListener("change", function() {
    hideOrShowFilePath();
  });
});
