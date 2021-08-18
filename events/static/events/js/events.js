// Submit an AJAX search form on 'all events' page
$('#event_search_form').submit(function (e) {
    e.preventDefault();
    var jsonData = $(this).serialize();
    $.ajax({
        type: 'POST',
        datatype: 'json',
        data: jsonData,
        url: $(this).attr('action'),
        timeout: 10000,
        success: function (data) {
            $('#search_results').html(data);
        },
        error: function (data) {
            console.log("There has been an error")
        }
    })
});


/***  
*** Event Registration Actions
***/

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

// Cancel event registration
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

// Change the registered / unregister button on event card
function changeButtonUI(buttonId, type) {
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
    $('.event-card-buttons button').mouseleave(function(){
        if($(this).hasClass('remove-reg-btn')){
            $(this).html('<i class="fas fa-check"></i>Registered');
        }
    })  
})();


/***
 *** Add / remove connections from events pages
 ***/


 // Add user as connection
function add_friend(other_user) {
    $.ajax({
        type: 'GET',
        url: `../ajax/add_friend/${other_user}`,
        timeout: 10000,
        success: function (data) {
            console.log("The response: ", data.response);
            changeConnectionButtonUI(data.buttonId, data.type);
        },
        error: function (data) {
            console.log("There has been an error")
        }
    })
};

// Cancel pending request
function cancel_friend(other_user) {
    var user_int = parseInt(other_user)
    $.ajax({
        type: 'GET',
        url: `../ajax/cancel_friend/${user_int}`,
        timeout: 10000,
        success: function (data) {
            changeConnectionButtonUI(data.buttonId, data.type);
        },
        error: function (data) {
            console.log("There has been an error")
        }
    })
};


// Accept pending request
function accept_friend(other_user) {
    var user_int = parseInt(other_user)
    $.ajax({
        type: 'GET',
        url: `../ajax/accept_friend/${user_int}`,
        timeout: 10000,
        success: function (data) {
            console.log("Friend accepted")
            changeConnectionButtonUI(data.buttonId, data.type);
        },
        error: function (data) {
            console.log("There has been an error")
        }
    })
};

// Decline pending request
function decline_friend(other_user) {
    var user_int = parseInt(other_user)
    $.ajax({
        type: 'GET',
        url: `../ajax/decline_friend/${user_int}`,
        timeout: 10000,
        success: function (data) {
            console.log("Friend declined")
            changeConnectionButtonUI(data.buttonId, data.type);
        },
        error: function (data) {
            console.log("There has been an error")
        }
    })
};

// Remove existing connection
function remove_friend(other_user) {
    var user_int = parseInt(other_user)
    $.ajax({
        type: 'GET',
        url: `../ajax/remove_friend/${user_int}`,
        timeout: 10000,
        success: function (data) {
            console.log("Friend removed")
            changeConnectionButtonUI(data.buttonId, data.type);
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
function changeConnectionButtonUI(buttonId, type) {
    console.log(type)
    // let buttonTarget = $(`.send-connection-btn[value="${buttonId}"]`);
    $(buttonTarget).text('Connection Request Sent');
    $(buttonTarget).removeClass('send-connection-btn').addClass('req-sent-btn');
    $(buttonTarget).attr('onclick', `cancel_friend(${buttonId});`);

    if (type == "cancel") {
        var buttonTarget = $(`.req-sent-btn[value="${buttonId}"]`);
        $(buttonTarget).text('Send Connection Request');
        $(buttonTarget).addClass('send-connection-btn').removeClass('req-sent-btn');
        $(buttonTarget).attr('onclick', `add_friend(${buttonId});`);
    } else if (type == "accept" || type == "decline"){
        $(`.conn-request-item[value="${buttonId}"]`).fadeOut("fast", "linear") 
        console.log("got you")
    } else if (type == "remove"){
        var buttonTarget = $(`.remove-connection-btn[value="${buttonId}"]`);
        $(buttonTarget).html('Connection Removed');
        $(buttonTarget).addClass('muted').removeClass('remove-connection-btn');
        $(buttonTarget).attr('onclick', ``);
        console.log("got you")
    }
};


// Change connection action button on hover, advising to user what clicking button will do
(function changeButtonTextFriend(){
    $('.connection-action-btns button').mouseenter(function(){
        console.log("working")
        if($(this).hasClass('remove-connection-btn')){
            $(this).html('<i class="fas fa-times"></i>Remove Connection');
            console.log("working", $(this).text())
        }
    });
    $('.connection-action-btns button').mouseleave(function(){
        if($(this).hasClass('remove-connection-btn')){
            $(this).html('<i class="fas fa-user"></i>Aleady Connected');
        }
    });
})();