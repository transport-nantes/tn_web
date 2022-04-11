/*
This script is used to display the number of recipients before
sending a TBEmail object to a mailing list, and ask for confirmation
*/

// Initial state
document.getElementById('nb-recipients').innerHTML = "0";
document.getElementById("send-email-btn").disabled = true;

async function get_number_of_recipients(mailing_list_token) {
    let response = await $.ajax({
        url: '/tb/ajax/get-number-of-recipients/' + mailing_list_token + '/',
        method: 'GET',
    })
    return response;
}

//// This Event listener updates the number of recipients message upon selection
//// of a mailing list
// This fires when we select a mailing list in the dropdown menu
document.getElementById('id_mailing_list').addEventListener('change', function() {
    let mailing_list_token = this.value;
    // We uncheck the confirmation box if it was checked, to make sure user
    // confirms its selection and not a previous one.
    document.getElementById('id_confirmation_box').checked = false;
    if (!mailing_list_token) {
        document.getElementById('nb-recipients').innerHTML = "0";
        document.getElementById("send-email-btn").disabled = true;
    }
    // Sends the mailing_list_token to the server to get the number of recipients
    get_number_of_recipients(mailing_list_token).then(function(response) {
        // The response is a dict with a key "count" and a value of the number of recipients
        let number_of_recipients = response.count;
        // The number_of_recipients is identified and isolated in the id "nb-recipients"
        // We replace its value with the one received from the server.
        document.getElementById("nb-recipients").innerHTML = number_of_recipients;
        number_of_recipients = parseInt(number_of_recipients);
        // If the number of recipients is 0, we disable the send-email-btn
        if (number_of_recipients == 0) {
            document.getElementById("send-email-btn").disabled = true;
        }
        else {
            document.getElementById("send-email-btn").disabled = false;
        }
    });
});

// This fires only when the "Envoyer" button is clicked
document.getElementById('send-email-btn').addEventListener('click', async function (event) {
    // Prevent the button to POST
    event.preventDefault();
    console.log("Listener fired")
    // Checks that the "id_confirmation_box" is checked
    if (document.getElementById('id_confirmation_box').checked) {
        number_of_recipients = parseInt(document.getElementById("nb-recipients").innerHTML);
        if (number_of_recipients > 0) {
            let send_button = document.getElementById('send-email-btn');
            send_button.disabled = true;
            send_button.innerHTML = 'Envoi en cours...';
            document.getElementById('send-email-form').submit();
        }
    } else {
        alert("Veuillez cocher la case pour confirmer l'envoi de l'email");
        return;
    }
})
