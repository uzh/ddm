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
});
