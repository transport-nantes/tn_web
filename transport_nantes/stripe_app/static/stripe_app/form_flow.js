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
            document.getElementById("real_cost").innerHTML = ""
            MakeNotRequiredByName("payment_amount", true)
            MakeNotRequiredByName("subscription_amount", false) 
        }
    })
})
