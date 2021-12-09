$(document).ready(function() {
    // Initialise the table
    $('#page-table').tableDnD({
        onDrop: function (table, row) {
            let i = 1;
            $(table).find('tbody').children('tr.page-row').each(function () {
                let index = $(this).children('.field-index').find('input').val(i);
                i = i + 1;
            });
        },
        dragHandle: '.drag-handle',
        sensitivity: 0,
    });

    $('.drag-handle').mousedown(function() {
        $(this).css('cursor', 'move');
    });
    $('.drag-handle').mouseup(function() {
        $(this).css('cursor', 'grab');
    });


    $('.sortable-pages').sortable({
        stop: function( event, ui ) {
            let par = ui.item.parent();
            let i = 1;
            par.find('div.sortable-row').each(function () {
                let index = $(this).children('.field-index').find('input').val(i);
                i = i + 1;
            });
        },
        handle: '.page-handle',
    });

    $('.sortable-questions').sortable({
        connectWith: '.sortable-questions',
        stop: function( event, ui ) {
            let par = ui.item.parent();

            $('.sortable-questions').each(function () {
                let i = 1;
                $(this).find('.field-q-index').each(function() {
                    $(this).find('input').val(i);
                    i = i + 1
                });
            });
        },
        handle: '.question-handle',
    });
});
