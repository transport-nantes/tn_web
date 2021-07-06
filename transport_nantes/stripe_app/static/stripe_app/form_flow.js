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
        document.getElementById("step1_text_2").classList.add("active")
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
    console.log("Return Button clicked !")
    document.getElementById("donation_form").style.display = "none"
    document.getElementById("amount_form").style.display = "block"
    document.getElementById("step1_text_2").classList.remove("active")
})

// Get Stripe publishable key
fetch("/donation/config/")
.then((result) => { return result.json(); })
.then((data) => {
  // Initialize Stripe.js
  const stripe = Stripe(data.publicKey);

// Upon support button click, forms data will be sent
  document.querySelector("#donation_form").addEventListener("submit", () => {
    
    if (valid_donation_form == true){
        document.getElementById("step1_text_3").classList.add("active")
        // Get Checkout Session ID
        form_data = new FormData(document.getElementById("amount_form"))

        form_data.append("mail", document.getElementById("id_mail").value)
        form_data.append("first_name", document.getElementById("id_first_name").value)
        form_data.append("last_name", document.getElementById("id_last_name").value)
        form_data.append("telephone", document.getElementById("id_cell_phone").value)
        form_data.append("gender", document.querySelector('input[name="gender"]:checked').value)
        form_data.append("address", document.getElementById("id_address").value)
        form_data.append("more_adress", document.getElementById("id_more_address").value)
        form_data.append("postal_code", document.getElementById("id_postal_code").value)
        form_data.append("city", document.getElementById("id_city").value)
        form_data.append("country", document.getElementById("id_country").value)


        fetch("/donation/create-checkout-session/", {
            body: form_data,
            method:"POST"})
        .then((result) => { return result.json(); })
        .then((data) => {
        console.log("Session ID :", data);
        // Redirect to Stripe Checkout
        return stripe.redirectToCheckout({sessionId: data.sessionId})
        })
        .then((res) => {
        console.log(res);
        });
    }
  });
});

window.addEventListener("beforeunload", function(event) {
    // Code to run upon closure, will fetch a function on
    // server and see how far the visitor went
    csrftoken=document.getElementsByName("csrfmiddlewaretoken")[0].value
    myHeaders = new Headers()
    myHeaders.append("X-CSRFToken", csrftoken)
    
    var form_progression = new FormData();
    form_progression.append("step_1_completed", step_1_completed)
    form_progression.append("step_2_completed", step_2_completed)
   
    fetch("/donation/tracking/", {
        headers: myHeaders,
        body: form_progression, 
        method:"POST",
        mode: "same-origin"
    })
    return false;
})