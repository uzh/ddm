document.getElementById("id_super_secret").addEventListener("change", function() {
  document.getElementById("id_project_password").value = "";
  document.getElementById("id_project_password_confirm").value = "";

  if (this.checked) {
    document.getElementById("secret-definition").classList.remove("d-none");
  } else {
    document.getElementById("secret-definition").classList.add("d-none");
  }
});
