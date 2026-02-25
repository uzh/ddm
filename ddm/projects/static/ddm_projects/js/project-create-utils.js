document.getElementById("id_super_secret").addEventListener("change", function() {
  document.getElementById("id_project_password").value = "";
  document.getElementById("id_project_password_confirm").value = "";

  const secretContainer = document.getElementById("secret-definition");

  if (this.checked && secretContainer) {
    secretContainer.style.opacity = "1";
    secretContainer.style.visibility = "visible";
    secretContainer.style.maxHeight = "500px";

  } else {
    secretContainer.style.opacity = "0";
    secretContainer.style.visibility = "hidden";
    secretContainer.style.maxHeight = "0";
  }
});


document.addEventListener('DOMContentLoaded', function() {
  const secretContainer = document.getElementById("secret-definition");
  if (secretContainer) {
    secretContainer.style.transition = "opacity 0.3s ease, visibility 0.3s ease, max-height 0.5s ease";
  }

  const secretToggle = document.getElementById("id_super_secret");
  if (secretToggle.checked && secretContainer) {
    secretContainer.style.opacity = "1";
    secretContainer.style.visibility = "visible";
    secretContainer.style.maxHeight = "500px";

  } else {
    secretContainer.style.opacity = "0";
    secretContainer.style.visibility = "hidden";
    secretContainer.style.maxHeight = "0";
  }

});