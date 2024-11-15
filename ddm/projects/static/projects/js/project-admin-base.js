function closeMessage(messageID) {
    const element = document.getElementById(messageID);
    element.remove();
}

$( document ).ready(function() {
    $("input[type=checkbox]").each(function() {
        let $lbl = $("<label>");
        $lbl.attr("for", this.id);
        $lbl.attr("class", "checkmark")
        $(this).after($lbl);
    });

    $(".ddm-message").each(function() {
      $(this).animate({opacity: 1, top: 0}, 300);
      setTimeout(() => {  $(this).animate({opacity: 0, top: -50}, 300); }, 7000);
    })
});
