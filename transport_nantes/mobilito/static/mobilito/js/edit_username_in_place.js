/*
This scripts allows users to edit their username in place.
This mean that they can click on their username and edit it,
without having to go to the profile page.
*/

document.addEventListener("DOMContentLoaded", function(event) {

    const USERNAME_EDIT_BTN_PREFIX = 'mobilito-username-edit-btn_';
    const USERNAME_EDIT_FORM_PREFIX = 'mobilito-username-edit-form_';
    const DISPLAYED_USERNAME_STRING_ID_PREXIF = 'displayed-username_';
    const CANCEL_BUTTON_PREFIX = 'mobilito-username-cancel-btn_';
    const FORM_ID_PREFIX = 'mobilito-username-edit-form_';

    // Edit buttons are identified by the id "USERNAME_EDIT_BTN_PREFIX_XXX"
    // where XXX is the session's SHA1.
    var all_edit_buttons = document.querySelectorAll(`[id^="${USERNAME_EDIT_BTN_PREFIX}"]`);
    all_edit_buttons.forEach(function(edit_button) {
        edit_button.addEventListener('click', function(e) {
            var session_sha1 = edit_button.id.split('_')[1];
            var form_id = USERNAME_EDIT_FORM_PREFIX + session_sha1;
            var displayed_username_string_id = DISPLAYED_USERNAME_STRING_ID_PREXIF + session_sha1;
            // Visible by default
            toggleVisibility(edit_button.id);
            toggleVisibility(displayed_username_string_id);
            // Hidden by default
            toggleVisibility(form_id);
        });
    });

    var all_cancel_buttons = document.querySelectorAll(`[id^="${CANCEL_BUTTON_PREFIX}"]`);
    all_cancel_buttons.forEach(function(cancel_button) {
        cancel_button.addEventListener('click', function(e) {
            var session_sha1 = cancel_button.id.split('_')[1];
            var form_id = USERNAME_EDIT_FORM_PREFIX + session_sha1;
            var displayed_username_string_id = DISPLAYED_USERNAME_STRING_ID_PREXIF + session_sha1;
            var edit_button_id = USERNAME_EDIT_BTN_PREFIX + session_sha1;
            // Visible when cancel button is visible
            toggleVisibility(form_id);
            // Hidden when cancel button is visible
            toggleVisibility(displayed_username_string_id);
            toggleVisibility(edit_button_id);
        });
    });

    var all_forms = document.querySelectorAll(`[id^="${FORM_ID_PREFIX}"]`);
    all_forms.forEach(function(form) {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            var post_url = form.getAttribute('action');
            var form_data = new FormData(form);

            $.ajax({
                type: 'POST',
                url: post_url,
                data: form_data,
                processData: false,
                contentType: false,
                mode: 'same-origin',
                success: () => {
                    window.location.reload(true);
                },
            });
        });
    });

});

function toggleVisibility(element_id) {
    var e = document.getElementById(element_id);
    e.classList.toggle('d-none');
}
