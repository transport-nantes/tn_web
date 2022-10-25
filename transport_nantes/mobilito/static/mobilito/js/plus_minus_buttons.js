$(document).ready(function(){

    var last_event = '';

    function plus_button_click(e) {
        e.preventDefault();
        if (last_event == 'touchend' && e.type == 'click') {
            return;
        }
        // Get the field name
        fieldName = $(this).attr('data-field');
        // Get its current value
        var currentVal = parseInt($('input[name='+fieldName+']').val());
        var newValue = currentVal + 1;
        // If is not undefined
        if (!isNaN(currentVal)) {
            // Update the value
            $('input[name='+fieldName+']').val(newValue);
            $('span[name='+fieldName+'-counter]').text(newValue);
            // Send event to server
            console.log(`Sending event to server`)
            $.ajax({
                url: '/mobilito/ajax/create-event/',
                headers: {"X-CSRFToken": getCookie("csrftoken")},
                type: 'post',
                data: {
                    event_type: fieldName,
                },
            });
        } else {
            // Otherwise put a 0 there
            $('input[name='+fieldName+']').val(0);
            $('span[name='+fieldName+'-counter]').text(0);
        }
        last_event = e.type;
        return false;
        
    }
    document.querySelectorAll('[data-quantity="plus"]').forEach(function(element) {
        element.addEventListener('click', plus_button_click);
        element.addEventListener('touchend', plus_button_click);
    })
});

