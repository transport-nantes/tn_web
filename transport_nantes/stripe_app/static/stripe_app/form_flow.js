// jQuery function to prevent form from submitting
// but allows Django's field validation
$(function(){
    $("#donation_form").submit(function(){
        return false
    })
})

// This function inputs a form and returns if it valid or not
// The listener_id is the id without #. ("id" instead of "#id")
async function validation_check(listener_id) {
    var valid = await fetch('form-validation/', {
        body: new FormData(document.getElementById(listener_id)),
        method: "POST"
    })
    .then((result) => {
        return(result.json())
    })
    .then((data) => {
        console.log("data are : ", data)
        if (data.validity == true) {
            console.log("The form is valid !")
            console.log("data.validity =", data.validity)
        }
        else {
            console.log("Invalid data !")
            console.log(data.validity)
        }
        return data.validity
    })
    return valid
}

// Button validating personnal informations step.
document.querySelector("#toStep2").addEventListener("click", async() => {
    console.log("Button clicked !");
    let valid = await validation_check("donation_form")
    if (valid == true) {
        console.log("validation in queryselector");
        document.getElementById("amount_form").style.display = "block"
        document.getElementById("donation_form").style.display = "none"
    }
    
})
// This button allows you to go back to the first step
document.querySelector("#toStep1").addEventListener("click", () => {
    console.log("Return Button clicked !")
    document.getElementById("donation_form").style.display = "block"
    document.getElementById("amount_form").style.display = "none"
})

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

// Adds an event listener to each html object with name="donation_type"
// The value is then evaluated to display appropriate amounts.
document.getElementsByName("donation_type").forEach(item => {
    item.addEventListener('click', event => {
        let selected = donation_selected()
        document.getElementById("free_amount").style.display = "block"
        if (selected == "payment") {
            document.getElementById("subscription_amount_rb").style.display = "none"
            document.getElementById("payment_amount_rb").style.display = "block"
        } else {
            document.getElementById("subscription_amount_rb").style.display = "block"
            document.getElementById("payment_amount_rb").style.display = "none"
        }
    })
})