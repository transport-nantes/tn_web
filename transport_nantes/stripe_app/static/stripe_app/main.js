// static/main.js

console.log("Sanity check!");

// Blocks the form from redirecting
// Also allows Django to perorm input validation
$(function(){
    $("#donation_form").submit(function(){
        return false
    })
})
// Get Stripe publishable key
fetch("/donation/config/")
.then((result) => { return result.json(); })
.then((data) => {
  // Initialize Stripe.js
  const stripe = Stripe(data.publicKey);

  // new
  // Event handler
  document.querySelector("#supportButton").addEventListener("click", () => {
    // Get Checkout Session ID
    fetch("/donation/create-checkout-session/", {
          body: new FormData(document.getElementById("donation_form")),
          method:"POST"})
    .then((result) => { return result.json(); })
    .then((data) => {
      console.log(data);
      // Redirect to Stripe Checkout
      return stripe.redirectToCheckout({sessionId: data.sessionId})
    })
    .then((res) => {
      console.log(res);
    });
  });
});