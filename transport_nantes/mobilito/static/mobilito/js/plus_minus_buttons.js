function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

$(document).ready(function(){
    // This button will increment the value
    $('[data-quantity="plus"]').click(function(e){
        // Stop acting like a button
        e.preventDefault();
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
    });
    // THERE IS NO MINUS BUTTON FOR NOW
    // I'm leaving this piece of code in case we want to add some way to
    // decrement the value later on.
    // This button will decrement the value till 0
    $('[data-quantity="minus"]').click(function(e) {
        // Stop acting like a button
        e.preventDefault();
        // Get the field name
        fieldName = $(this).attr('data-field');
        // Get its current value
        var currentVal = parseInt($('input[name='+fieldName+']').val());
        var newValue = currentVal - 1;
        // If it isn't undefined or its greater than 0
        if (!isNaN(currentVal) && newValue >= 0) {
            // Decrement one
            $('input[name='+fieldName+']').val(newValue);
            $('span[name='+fieldName+'-counter]').text(newValue);
        } else {
            // Otherwise put a 0 there
            $('input[name='+fieldName+']').val(0);
            $('span[name='+fieldName+'-counter]').text(0);
        }
    });
});

