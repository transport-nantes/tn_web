$(document).ready(function () {
    const DEFAULT_SLUG = $('#id_slug').val();
    console.log(DEFAULT_SLUG)
    $('#id_slug').on('input', function () {
        if (DEFAULT_SLUG != $(this).val() && !$('#slug_change_warning').length) {
            $('#id_slug').after("<span class='small text-danger' id='slug_change_warning'><i class='fas fa-exclamation-triangle'></i> vous êtes sur le point de modifier le slug</span>");
        }else if (DEFAULT_SLUG == $(this).val() && $('#slug_change_warning').length){
            $("#slug_change_warning").remove();
        }
    });
});
