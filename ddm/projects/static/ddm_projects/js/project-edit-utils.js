function hideOrShowParameter() {
    if( $( "#id_url_parameter_enabled" ).is(":checked")) {
        $( "#id_expected_url_parameters" ).parent().show();
    } else {
        $( "#id_expected_url_parameters" ).parent().hide();
    }
}

function hideOrShowRedirect() {
    if( $( "#id_redirect_enabled" ).is(":checked")) {
        $( "#id_redirect_target" ).parent().show();
    } else {
        $( "#id_redirect_target" ).parent().hide();
    }
}

$(function() {
    hideOrShowParameter();
    hideOrShowRedirect();
});

$( "#id_url_parameter_enabled" ).change(function() { hideOrShowParameter() });
$( "#id_redirect_enabled" ).change(function() { hideOrShowRedirect() });

$(document).ready(function () {
    $('.ddm-accordion-btn').on("click", function () {
        if ($(this).attr('aria-expanded') === 'true') {
            $(this).addClass('sign-accordion-open');
        } else {
            $(this).removeClass('sign-accordion-open');
        }
    });
});
