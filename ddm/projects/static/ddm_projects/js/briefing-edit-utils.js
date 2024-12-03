function hideOrShowConsentLabels() {
    if( $( "#id_briefing_consent_enabled" ).is(":checked")) {
        $( "#id_briefing_consent_label_yes" ).parent().show();
        $( "#id_briefing_consent_label_no" ).parent().show();
    } else {
        $( "#id_briefing_consent_label_yes" ).parent().hide();
        $( "#id_briefing_consent_label_no" ).parent().hide();
    }
}

$(function() {
    hideOrShowConsentLabels();
});

$( "#id_briefing_consent_enabled" ).change(function() { hideOrShowConsentLabels() });