document.addEventListener("DOMContentLoaded", function() {
  document.querySelectorAll(".ddm-accordion-item").forEach(function(accordion) {
    const hasError = accordion.querySelector('.errorlist');
    if (hasError) {
      accordion.classList.add('has-error');

      const button = accordion.querySelector(".ddm-accordion-btn");
      if (button) {
        button.classList.remove("collapsed");
        button.ariaExpanded = "true";
      }

      const accordionBody = accordion.querySelector(".accordion-collapse");
      if (accordionBody) {
        accordionBody.classList.add("show");
      }
    }
  });
});
