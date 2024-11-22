const file_uploader_meta = JSON.parse(document.getElementById("file_uploader_meta").textContent);

function hideOrShowCsvDelimiter() {
    if( $( "#id_exp_file_format" ).val() === "csv") {
        $( "#id_csv_delimiter" ).parent().show();
    } else {
        $( "#id_csv_delimiter" ).parent().hide();
    }
}

function hideOrShowRegexPath() {
    if( file_uploader_meta[$( "#id_file_uploader" ).val()] === "zip file" ) {
        $( "#id_regex_path" ).parent().show();
    } else {
        $( "#id_regex_path" ).parent().hide();
    }
}

function hideOrShowJsonRoot() {
    if( $( "#id_exp_file_format" ).val() === "json") {
        $( "#id_json_extraction_root" ).parent().show();
    } else {
        $( "#id_json_extraction_root" ).parent().hide();
    }
}

$(function() {
    hideOrShowCsvDelimiter();
    hideOrShowRegexPath();
    hideOrShowJsonRoot();
});

$( "#id_exp_file_format" ).change(function() {
    hideOrShowCsvDelimiter();
    hideOrShowJsonRoot();
});

$( "#id_file_uploader" ).change(function() {
    hideOrShowRegexPath()
});
