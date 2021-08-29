var stripePublicKey = $('#id_stripe_public_key').text().slice(1, -1);
var stripeClientSecret = $('#id_stripe_client_secret').text().slice(1, -1);
var is_upgrade = $('#is_upgrade').val();
var stripe = Stripe(stripePublicKey);
var elements = stripe.elements();

let card = elements.create('card');
card.mount('#card_element');


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
$('#submit_button').on('click', async (event) => {
    event.preventDefault();

    card.update({ 'disabled': true })
    $('.processing-spinner').css('display', 'flex').hide().fadeIn();
    $('#submit_button').attr('disabled', true);
    $('#submit_button').addClass('disabled');

    stripe.confirmCardPayment(stripeClientSecret, {
        payment_method: {
            card: card,
            billing_details: {
                name: "bradley",
            }
        },
    }).then(function (result) {
        var errorDiv = $('#card_errors')
        if (result.error) {
            var html = `
            <span class="icon" role="alert">
            <i class="fas fa-times"></i>
            </span>
            <span>${result.error.message}</span>
            `
            card.update({ 'disabled': false });
            errorDiv.html(html);
            $('.processing-spinner').fadeOut();
            $('#submit_button').attr('disabled', false);
            $('#submit_button').removeClass('disabled');
        } else {
            errorDiv.text = ""
            if (result.paymentIntent.status === 'succeeded') {
                var formSubmitted = true
                $('#payment_form').submit()

            }
        }
    });
});