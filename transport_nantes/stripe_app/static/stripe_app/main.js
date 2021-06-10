// static/main.js

console.log("Sanity check!");

// Blocks the form from redirecting
// Also allows Django to perorm input validation
$(function(){
    $("#amount_form").submit(function(){
        return false
    })
})

// Get Stripe publishable key
fetch("/donation/config/")
.then((result) => { return result.json(); })
.then((data) => {
  // Initialize Stripe.js
  const stripe = Stripe(data.publicKey);

// Upon support button click, forms data will be sent
  document.querySelector("#supportButton").addEventListener("click", () => {
    // Get Checkout Session ID
    form_data = new FormData(document.getElementById("amount_form"))
    form_data.append("mail", document.getElementById("id_mail").value)
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
  });
});