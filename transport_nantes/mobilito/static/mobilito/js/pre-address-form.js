$(document).ready(function() {
    
    const hide_pre_form = () => {
        //Play css animation
        $('#pre-address-form').toggleClass('hidden');
        setTimeout(() => {
            // Remove pre form from the display
            $('#pre-address-form').toggleClass('d-flex');
            $('#pre-address-form').addClass('d-none');
            // Show the form
            $('#address-form').toggleClass('active');
        }, 500);
    }

    $('[name="address-form-yes"]').on('click', hide_pre_form);
    $('[name="address-form-yes"]').on('tap', hide_pre_form);

});