/*
This script is used to display the number of recipients before
sending a TBEmail object to a mailing list, and ask for confirmation
*/


async function get_number_of_recipients(mailing_list_token) {
    let response = await $.ajax({
        url: '/tb/ajax/get-number-of-recipients/' + mailing_list_token + '/',
        method: 'GET',
    })
    return response;
}

// This fires only when the "Envoyer" button is clicked
document.getElementById('send-email-btn').addEventListener('click', async function (event) {
    // Prevent the button to POST
    event.preventDefault();
    // Get the selected value in the dropdown
    let mailing_list_token = document.getElementById('id_mailing_list').value;
    // Result of the Ajax request is a dict {"count" : <int:number_of_recipients>}
    let number_of_recipients = await get_number_of_recipients(mailing_list_token);
    number_of_recipients = number_of_recipients["count"];
    if (number_of_recipients > 0) {
        // Display a confirmation alert with OK and cancel,if OK is clicked, it evaluates to True.
        if (confirm("Vous êtes sur le point d'envoyer un email à " + number_of_recipients + " destinataires.\n\n" +
            "Êtes-vous sûr de vouloir continuer ?") == true) {
            // If OK is clicked, we submit the form with a visual feedback
            document.getElementById('send-email-btn').disabled = true;
            document.getElementById('send-email-btn').innerHTML = 'Envoi en cours...';
            document.getElementById('send-email-form').submit();
        };
    } else {
        alert("Aucun destinataire n'a été trouvé.\n\n");
    }
})
