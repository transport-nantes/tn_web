console.log("integrated script launch")

// Item purchased
var purchase = {
    items: [{ id: "donation_10"}]
};

// get the publicKey and create a Stripe.js instance
fetch("checkout/config/")
    .then((result) => { 
        return result.json();
    })
    .then((data) => {
        // Initialize Stripe.js
        let stripe = Stripe(data.publicKey);
        // DEBUG
        console.log("Data.publicKey :", data.publicKey);
        console.log("stripe value is :", stripe)
        console.log("instance of stripe.elements : ", typeof stripe.elements)

        document.querySelector("button").disabled = true;

        fetch("/checkout/create-payment-intent/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify(purchase)
        })
        .then(function (result) {
            return result.json();
        })
        .then(function (data) {
            var elements = stripe.elements();
            var style = {
                base: {
                  color: "#32325d",
                  fontFamily: 'Arial, sans-serif',
                  fontSmoothing: "antialiased",
                  fontSize: "16px",
                  "::placeholder": {
                    color: "#32325d"
                  }
                },
                invalid: {
                  fontFamily: 'Arial, sans-serif',
                  color: "#fa755a",
                  iconColor: "#fa755a"
                }
          
              };
              var card = elements.create("card", { style: style });
              // Stripe injects an iframe into the DOM
              card.mount("#card-element");
          
              card.on("change", function (event) {
                // Disable the Pay button if there are no card details in the Element
                document.querySelector("button").disabled = event.empty;
                document.querySelector("#card-error").textContent = event.error ? event.error.message : "";
              });
          
              var form = document.getElementById("payment-form");
              form.addEventListener("submit", function(event) {
                event.preventDefault();
                // Complete payment when the submit button is clicked
                payWithCard(stripe, card, data.clientSecret);
              });
          
        });

            });

var payWithCard = function(stripe, card, clientSecret) {
loading(true);
stripe
    .confirmCardPayment(clientSecret, {
    payment_method: {
        card: card
    }
    })
    .then(function(result) {
    if (result.error) {
        // Show error to your customer
        showError(result.error.message);
    } else {
        // The payment succeeded!
        orderComplete(result.paymentIntent.id);
    }
    });
};

/* ------- UI helpers ------- */

// Shows a success message when the payment is complete
var orderComplete = function(paymentIntentId) {
loading(false);
document
    .querySelector(".result-message a")
    .setAttribute(
    "href",
    "https://dashboard.stripe.com/test/payments/" + paymentIntentId
    );
document.querySelector(".result-message").classList.remove("hidden");
document.querySelector("button").disabled = true;
};

// Show the customer the error from Stripe if their card fails to charge
var showError = function(errorMsgText) {
loading(false);
var errorMsg = document.querySelector("#card-error");
errorMsg.textContent = errorMsgText;
setTimeout(function() {
    errorMsg.textContent = "";
}, 4000);
};

// Show a spinner on payment submission
var loading = function(isLoading) {
if (isLoading) {
    // Disable the button and show a spinner
    document.querySelector("button").disabled = true;
    document.querySelector("#spinner").classList.remove("hidden");
    document.querySelector("#button-text").classList.add("hidden");
} else {
    document.querySelector("button").disabled = false;
    document.querySelector("#spinner").classList.add("hidden");
    document.querySelector("#button-text").classList.remove("hidden");
}
};




