// Hides the navbar's content in this page
nav = document.querySelector(".navbar-nav")
nav.style = "display: none"

/* 
This places an even listener on each radio_button
Everytime a radio is pressed on the page, the script
will check for each button if it's checked.
If checked, background changes. 
*/
document.querySelectorAll("input[type='radio']").forEach((item, index) => {
    item.addEventListener("click", event => {
        update_style()
    })
})

$('#free_amount').on('click', function() {
    update_style()
});

radio_buttons = document.querySelectorAll("input[type='radio']")

function update_style() {
    radio_buttons.forEach(item => {
        if (item.checked == true) {
            item.parentNode.style = "background-color: var(--mobilitains-bleu)"
        } else {
            item.parentNode.style = "background-color: white"
        }
    })
}
