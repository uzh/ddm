function hideOrShowZipConfig() {
  const expFileFormat = document.getElementById("id_upload_type").value;

  const extractNestedRootParent = document.getElementById("id_extract_nested_zips").parentNode;
  const extractDepthRootParent = document.getElementById("id_extraction_depth").parentNode;

  if (expFileFormat === "zip file") {
    extractNestedRootParent.style.display = "";
    extractDepthRootParent.style.display = "";
  } else {
    extractNestedRootParent.style.display = "none";
    extractDepthRootParent.style.display = "none";
  }
}

document.addEventListener("DOMContentLoaded", function() {
  hideOrShowZipConfig();

  document.getElementById("id_upload_type").addEventListener("change", function() {
    hideOrShowZipConfig();
  });

});
