function reset_html(id) {
    $('#' + id).html($('#' + id).html());
    return false;
}

$(document).ready(function () {

    var file_input_index = 0;
    $('input[type=file]').each(function () {
        file_input_index++;
        $(this).wrap('<div id="file_input_container_' + file_input_index + '"></div>');
        $(this).after('<u><a href="#" '
        + 'onclick="reset_html(\'file_input_container_' + file_input_index + '\');"'
        + 'class="small text-dark my-1">' + 'Supprimer l\'image' + '</a></u>');
    });

});
