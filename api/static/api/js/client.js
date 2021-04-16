// A reference to Stripe.js initialized with a fake API key.
// Sign in to see examples pre-filled with your key.
var stripe = Stripe("pk_test_51IGkXjHRg08Ncmk7fPlbb9DfTF5f7ckXBKiR4g01euLgXs04CqmgBPOQuqQfOhc6aj9mzsYE1oiQ3TFjHH9Hv3Mj00GNyG9sep");
// The items the customer wants to buy

var formdata = new FormData();
formdata.append("password", "ameba12345");
formdata.append("email", "web_user@ameba.cat");

var requestOptions = {
  method: 'POST',
  body: formdata,
  redirect: 'follow'
};


// Disable the button until we have Stripe set up on the page
document.querySelector("button").disabled = true;
fetch("http://localhost:8000/api/token/", requestOptions)
  .then(function(response) {
    return response.json();
  })
  .then(function (token) {
    fetch("/api/carts/current/checkout/", {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + token.access
      },
      // body: JSON.stringify(purchase)
    })
        .then(function (result) {
          return result.json();
        })
        .then(function (data) {

          // Información sobre el pago directamente de la respuesta de la API
          var amount_element = document.getElementById("total-amount")
          amount_element.innerText = 'Total: ' + data.amount / 100. + ' €'
          console.log(amount_element.innerText)

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
          var card = elements.create("card", {style: style});
          // Stripe injects an iframe into the DOM
          card.mount("#card-element");
          card.on("change", function (event) {
            // Disable the Pay button if there are no card details in the Element
            document.querySelector("button").disabled = event.empty;
            document.querySelector("#card-error").textContent = event.error ? event.error.message : "";
          });
          var form = document.getElementById("payment-form");
          form.addEventListener("submit", function (event) {
            event.preventDefault();
            // Complete payment when the submit button is clicked
            payWithCard(stripe, card, data.checkout.client_secret);
          });
        });
  });
// Calls stripe.confirmCardPayment
// If the card requires authentication Stripe shows a pop-up modal to
// prompt the user to enter authentication details without leaving your page.
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
        // Si el pago devuelve error, muestra el mensaje de error
        showError(result.error.message);
      } else {
          orderComplete(result.paymentIntent.id);
          // Si  el pago es ok, DELETE http://localhost:8000/api/carts/current/
          // autenticado.
          var requestOptions2 = {
            method: 'POST',
            body: formdata,
            redirect: 'follow'
          };

          fetch("http://localhost:8000/api/token/", requestOptions2)
            .then(function(response) {
              return response.json();
            })
            .then(function (token) {
                fetch("/api/carts/current/", {
                  method: "DELETE",
                  headers: {
                    "Content-Type": "application/json",
                    "Authorization": "Bearer " + token.access
                  },
                  // body: JSON.stringify(purchase)
                })
                  .then(response => response.text())
                  .then(result => console.log(result))
                  // The payment succeeded!
                  .catch(error => console.log('error', error));
            })
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
