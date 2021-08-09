// ############################################
// ######### Prevent default submits ##########
// ############################################

// Blocks the form from redirecting
// Also allows browser to perform input validation
$(function(){
    $("#donation_form").submit(function(){
        return false
    })
})

$(function(){
    $("#amount_form").submit(function(){
        return false
    })
})


// ############################################
// ######### AMOUNT FORM DISPLAY ##############
// ############################################

// This function will check what set of amount to display
// depending on what option is selected.
function donation_selected() {
    var donation_radios = document.getElementsByName("donation_type")
    let selected
    for (const radio_button of donation_radios) {
        if (radio_button.checked) {
            selected = radio_button.value
            break
        }
    }
    return selected
}

// Uses name to make fields not required.
// reverse is a bool to make the reverse action if true. 
function MakeNotRequiredByName(name, reverse) {
    document.getElementsByName(name).forEach(item => {
        if (reverse == true) {
            item.removeAttribute("required")
        } else {
            item.setAttribute("required", "true")
        }
        
    })
}

// Adds an event listener to each html object with name="donation_type"
// The value is then evaluated to display appropriate amounts.
document.getElementsByName("donation_type").forEach(item => {
    item.addEventListener('click', event => {
        let selected = donation_selected()
        if (selected == "payment") {
            document.getElementById("subscription_amount_rb").style.display = "none"
            document.getElementById("payment_amount_rb").style.display = "flex"
            document.getElementById("free_amount").style.display = "flex"
            MakeNotRequiredByName("subscription_amount", true)
            MakeNotRequiredByName("payment_amount", false)
        } else {
            document.getElementById("subscription_amount_rb").style.display = "flex"
            document.getElementById("payment_amount_rb").style.display = "none"
            document.getElementById("free_amount").style.display = "none"
            document.getElementById("free_amount").removeAttribute("required")
            document.getElementById("real_cost").innerHTML = ""
            MakeNotRequiredByName("payment_amount", true)
            MakeNotRequiredByName("subscription_amount", false) 
        }
    })
})
// Returns what button is selected in the one-time payments.
function payment_amount_selected() {
    var payment_radios = document.getElementsByName("payment_amount")
    let selected
    for (const radio_button of payment_radios) {
        if (radio_button.checked) {
            selected = radio_button.value
            break
        }
    }
    return selected
}
// Handles requirements if user picks one time payments. 
// This sets the free amount field to required / not required
// depending if the user selected free amount or not in radios buttons.
document.getElementsByName("payment_amount").forEach(item => {
    item.addEventListener("click", event => {
        let selected = payment_amount_selected()
        if (selected == "0") {
            document.getElementById("payment_amount_rb_3").setAttribute("checked", "true")
            document.getElementById("free_amount").setAttribute("required", "true")
        } else {
            document.getElementById("payment_amount_rb_3").removeAttribute("checked")
            document.getElementById("free_amount").removeAttribute("required")
        }
    })
})

// Add a message calculating actual cost of donation.
function real_cost_message(amount) {
    real_cost = document.getElementById("real_cost")
    real_cost.innerHTML = "Votre don ne vous revient qu'à " + parseFloat(amount/3).toFixed(2) + "€ après déduction d'impôts !"
}

// Event to trigger calculation and update the message when an amount is selected.
document.querySelectorAll("input[id*='payment_amount_rb']").forEach(item => {
    item.addEventListener("click", event => {
        // Clear message 
        document.getElementById("real_cost").innerHTML = ""
        if (event.target.value != 0) {
            // Generate a new message
            real_cost_message(event.target.value)
            // Clear the free amount field if not selected
            document.getElementById('free_amount').value = ""
        }
    })
})
// Compute the actual cost at the same time as user inputs in the free amount field
$('#free_amount').on('input', function() {
    // "Montant Libre" button
    checked_button = document.getElementById("payment_amount_rb_3")
    if (checked_button.checked) {
        free_amount = document.getElementById("free_amount").value
        real_cost_message(free_amount)
    }
})

// ############################################
// ######### Form validation part #############
// ############################################

/* 
https://developer.mozilla.org/en-US/docs/Web/API/HTMLFormElement/reportValidity
Checks validity of a form from HTML5. 
*/

var step_1_completed = false
var step_2_completed = false
// Hides part 1 and displays part 2.
var valid_amount_form = false
document.forms['amount_form'].addEventListener('submit', function() {
    valid_amount_form = document.forms['amount_form'].reportValidity();
    if (valid_amount_form == true) {
        document.getElementById("amount_form").style.display = "none"
        document.getElementById("donation_form").style.display = "block"
        document.getElementById("progress_bar_step_2").classList.add("active")
        step_1_completed = true
    }
  }, false);

// Performs validation. If the form is correct, datas can be sent to Stripe.
var valid_donation_form = false
document.forms['donation_form'].addEventListener('submit', function() {
    valid_donation_form = document.forms['donation_form'].reportValidity();
    if (valid_donation_form) {
        step_2_completed = true
    }
  }, false);

// ############################################
// ######### BUTTON MANAGEMENT PART ###########
// ############################################

// This button allows you to go back to the first step
document.querySelector("#toStep1").addEventListener("click", () => {
    document.getElementById("donation_form").style.display = "none"
    document.getElementById("amount_form").style.display = "block"
    document.getElementById("progress_bar_step_2").classList.remove("active")
})