// Get variables from template.
const file_uploader_meta = JSON.parse(document.getElementById("file_uploader_meta").textContent);

function hideOrShowCsvFields() {
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

  const fileIdZip = document.getElementById("file-identification-info-zip");
  const fileIdSingleFile = document.getElementById("file-identification-info-single-file");

  if (file_uploader_meta[fileUploaderVal] === "single file") {
    fileIdZip.classList.add("d-none");
    fileIdZip.classList.remove("d-block");
    fileIdSingleFile.classList.add("d-block");
    fileIdSingleFile.classList.remove("d-none");
  } else {
    fileIdZip.classList.add("d-block");
    fileIdZip.classList.remove("d-none");
    fileIdSingleFile.classList.add("d-none");
    fileIdSingleFile.classList.remove("d-block");
  }
}

function hideOrShowJsonFields() {
  const expFileFormat = document.getElementById("id_exp_file_format").value;

  const jsonParserFields = document.getElementById("json-parser-fields");

  if (jsonParserFields) {
    if (expFileFormat === "json") {
      jsonParserFields.style.display = "";
    } else {
      jsonParserFields.style.display = "none";
    }
  }
}

function hideOrShowNestedLoopDependentFields() {
  const expFileFormat = document.getElementById("id_exp_file_format").value;
  const nestedLoopPathField = document.getElementById("id_json_nested_loop_path");
  const nestedLoopPathSet = !!(nestedLoopPathField && nestedLoopPathField.value.trim() !== "");
  const shouldShow = expFileFormat === "json" && nestedLoopPathSet;

  // Fields only meaningful once a Nested loop path is configured.
  ["nested-expected-fields", "nested-display-settings"].forEach(function(id) {
    const el = document.getElementById(id);
    if (el) {
      el.style.display = shouldShow ? "" : "none";
    }
  });
}

function hideOrShowTxtFields() {
  const expFileFormat = document.getElementById("id_exp_file_format").value;

  const jsonExtractionRootParent = document.getElementById("txt-parser-fields");

  if (jsonExtractionRootParent) {
    if (expFileFormat === "txt") {
      jsonExtractionRootParent.style.display = "";
    } else {
      jsonExtractionRootParent.style.display = "none";
    }
  }
}

document.addEventListener("DOMContentLoaded", function() {
  hideOrShowCsvFields();
  hideOrShowFilePath();
  hideOrShowJsonFields();
  hideOrShowTxtFields();
  hideOrShowNestedLoopDependentFields();

  document.getElementById("id_exp_file_format").addEventListener("change", function() {
    hideOrShowCsvFields();
    hideOrShowJsonFields();
    hideOrShowTxtFields();
    hideOrShowNestedLoopDependentFields();
  });

  document.getElementById("id_file_uploader").addEventListener("change", function() {
    hideOrShowFilePath();
  });

  const nestedLoopPathField = document.getElementById("id_json_nested_loop_path");
  if (nestedLoopPathField) {
    nestedLoopPathField.addEventListener("input", function() {
      hideOrShowNestedLoopDependentFields();
    });
  }
});
