
// This script displays the project and/or the compensations
// depending on user's selection.
// It does so by adjusting the classes of the elements.

project_button = document.getElementById('Projet');
compensation_button = document.getElementById('Contreparties');
project_description = document.getElementById('main_body_cf');
compensation_description = document.getElementById('cards_holder');

project_button.addEventListener("click", event => {

    // Add or remove the bottom border signaling
    // the user's current selection
    project_button.classList.add("bot-border")
    compensation_button.classList.remove("bot-border")


    project_description.classList.remove("d-flex");
    project_description.style.display = "block";

    compensation_description.classList.remove("d-flex")
    compensation_description.style.display = "none";
})

compensation_button.addEventListener("click", event => {

    // Add or remove the bottom border signaling
    // the user's current selection
    project_button.classList.remove("bot-border")
    compensation_button.classList.add("bot-border")

    project_description.classList.remove("d-flex");
    project_description.style.display = "none";

    compensation_description.classList.remove("d-flex")
    compensation_description.style.display = "block";
})
