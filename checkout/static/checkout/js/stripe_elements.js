// Logic below from Stripe documentation here: https://stripe.com/docs/payments/accept-a-payment

var stripePublicKey = $('#id_stripe_public_key').text().slice(1, -1);
var stripeClientSecret = $('#id_stripe_client_secret').text().slice(1, -1);
var stripe = Stripe(stripePublicKey);
var elements = stripe.elements();
var card = elements.create('card');
card.mount('#card_element');

console.log(stripeClientSecret)


// Add errors to card handler

card.addEventListener('change', function (event) {
    var errorDiv = $('#card_errors')
    if (event.error) {
        var html = `
        <span class="icon" role="alert">
            <i class="fas fa-times"></i>
        </span>
        <span>${event.error.message}</span>
        `
        errorDiv.html(html);
    } else {
        errorDiv.text = ""
    }
})

// Handle form submit

var form = document.getElementById('payment_form');

form.addEventListener('submit', function (event) {
    event.preventDefault();
    card.update({ 'disabled': true })
    $('#submit_button').attr('disabled', true);
    stripe.confirmCardPayment(stripeClientSecret, {
        payment_method: {
            card: card
        }
    }).then(function (result) {
        var errorDiv = $('#card_errors')
        if (event.error) {
            var html = `
        <span class="icon" role="alert">
            <i class="fas fa-times"></i>
        </span>
        <span>${event.error.message}</span>
        `
            errorDiv.html(html);
            card.update({ 'disabled': false })
    $('#submit_button').attr('disabled', false);
        } else {
            errorDiv.text = ""
            if (result.paymentIntent.status === 'succeeded') {
                console.log("this worked")
                form.submit()
            }
        }
    })
})