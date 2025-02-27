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

function hideOrShowRegexPath() {
  const fileUploaderVal = document.getElementById("id_file_uploader").value;
  const regexPathParent = document.getElementById("id_regex_path").parentNode;

  if (file_uploader_meta[fileUploaderVal] === "zip file") {
    regexPathParent.style.display = "";
  } else {
    regexPathParent.style.display = "none";
  }
}

function hideOrShowJsonRoot() {
  const expFileFormat = document.getElementById("id_exp_file_format").value;
  const jsonExtractionRootParent = document.getElementById("id_json_extraction_root").parentNode;

  if (expFileFormat === "json") {
    jsonExtractionRootParent.style.display = "";
  } else {
    jsonExtractionRootParent.style.display = "none";
  }
}

document.addEventListener("DOMContentLoaded", function() {
  hideOrShowCsvDelimiter();
  hideOrShowRegexPath();
  hideOrShowJsonRoot();

  document.getElementById("id_exp_file_format").addEventListener("change", function() {
    hideOrShowCsvDelimiter();
    hideOrShowJsonRoot();
  });

  document.getElementById("id_file_uploader").addEventListener("change", function() {
    hideOrShowRegexPath();
  });
});
