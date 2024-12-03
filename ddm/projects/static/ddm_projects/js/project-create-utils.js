$( "#id_super_secret" ).change(function() {
    $( "#id_secret" ).val("");
    $( "#id_secret_confirm" ).val("");
    if( $( this ).is(":checked")) {
        $( "#secret-definition" ).show();
    } else {
        $( "#secret-definition" ).hide();
    }
})