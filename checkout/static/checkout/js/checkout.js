/* LAYOUT JS */

// Find current package and set card to active
var currentPackageTier = $('#id_current_package_tier').val();
var activePackageCard = $(`#tier_${currentPackageTier}_package`);
var activePackageCardLabel = $(`#tier_${currentPackageTier}_package > .current_package_label`);
var allPackageCardLabel = $(`.current_package_label`);
activePackageCard.addClass('active');
activePackageCardLabel.text('Your current package');
activePackageCardLabel.removeClass('hidden');

$('.update-package-card').on('click', function () {
    $(this).find('span:first').removeClass('hidden')
    if (this != activePackageCard) {
        activePackageCard.addClass('hlf-trans');
        $(activePackageCard).find('.update-package-card-overlay').css('opacity', '0.75');
        $(activePackageCard).css('color', 'var(--dark-text)');
    }
})


/* STRIPE ELEMENTS */

// Logic below from Stripe documentation here: https://stripe.com/docs/payments/accept-a-payment

var stripePublicKey = $('#id_stripe_public_key').text().slice(1, -1);
var stripeClientSecret = $('#id_stripe_client_secret').text().slice(1, -1);
var stripe = Stripe(stripePublicKey);
var elements = stripe.elements();

let card = elements.create('card');
card.mount('#card_element');

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
$('#payment_form').on('submit', function (event) {
    event.preventDefault();
    card.update({ 'disabled': true })
    $('#submit_button').attr('disabled', true);
    stripe.confirmCardPayment(stripeClientSecret, {
        payment_method: {
            card: card,
            billing_details: {
                name: "bradley",
            }
        },
    }).then(function (result) {
        var errorDiv = $('#card_errors')
        console.log(result)
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
                $('#payment_form').submit()
            }
        }
    })
});