// Register for event
function event_register(event_id) {
    var event_int = parseInt(event_id)
    $.ajax({
        type: 'GET',
        url: `/meetups/ajax/event_register/${event_int}`,
        timeout: 10000,
        success: function (data) {
            console.log("User successfully registered")
            changeButtonUI(data.buttonId, data.type);
        },
        error: function (data) {
            console.log("There has been an error")
        }
    })
};

// Decline pending request
function event_cancel(event_id) {
    var event_int = parseInt(event_id)
    $.ajax({
        type: 'GET',
        url: `/meetups/ajax/event_cancel/${event_int}`,
        timeout: 10000,
        success: function (data) {
            console.log("User successfully cancelled")
            changeButtonUI(data.buttonId, data.type);
        },
        error: function (data) {
            console.log("There has been an error")
        }
    })
};

// Set friendship buttons on each card on page load
(() => {
    $(`.req-sent-btn`).each(function () {
        var buttonId = $(this).val();
        $(`.send-connection-btn[value="${buttonId}"]`).remove();
    });
})();

// Change the friend 'connection' button on successful add
function changeButtonUI(buttonId, type) {
    console.log(buttonId, type)
    let buttonTarget = $(`.send-connection-btn[value="${buttonId}"]`);
    $(buttonTarget).text('Connection Request Sent');
    $(buttonTarget).removeClass('send-connection-btn').addClass('req-sent-btn');
    $(buttonTarget).attr('onclick', `cancel_friend(${buttonId});`);

    if (type == "register") {
        let buttonTarget = $(`.register-btn[value="${buttonId}"]`);
        $(buttonTarget).html('<i class="fas fa-check"></i>Registered');
        $(buttonTarget).addClass('remove-reg-btn').removeClass('register-btn');
        $(buttonTarget).attr('onclick', `event_cancel(${buttonId});`);
    } else if (type == "cancel_reg" || type == "decline"){
        let buttonTarget = $(`.remove-reg-btn[value="${buttonId}"]`);
        $(buttonTarget).html('<i class="fas fa-clipboard"></i>Register');
        $(buttonTarget).addClass('register-btn').removeClass('remove-reg-btn');
        $(buttonTarget).attr('onclick', `event_register(${buttonId});`);
        $(buttonTarget).mouseleave();
    }
};


// Change event action button on hover, advising to user what clicking button will do
(function changeButtonText(){
    $('.event-card-buttons button').mouseenter(function(){
        if($(this).hasClass('remove-reg-btn')){
            $(this).html('<i class="fas fa-times"></i>Cancel');
        }
    })
})();