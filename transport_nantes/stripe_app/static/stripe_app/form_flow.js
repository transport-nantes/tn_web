// jQuery function to prevent form from submitting
// but allows Django's field validation
$(function(){
    $("#donation_form").submit(function(){
        return false
    })
})

// This function inputs a form and returns if it valid or not
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
// function callValidation(listener_id) {await validation_check(listener_id)} 

document.querySelector("#donation_form").addEventListener("submit", () => {
    console.log("Submitted !")
})

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

document.querySelector("#toStep1").addEventListener("click", () => {
    console.log("Return Button clicked !")
    document.getElementById("donation_form").style.display = "block"
    document.getElementById("amount_form").style.display = "none"
})