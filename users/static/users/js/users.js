// Initialize on page load
$(document).ready(function () {
    // Check screen width and remove active from sidenav if mobile
    if (screenWidth > 991.98) {
        $('#sidebar_wrap').addClass('active')
    };
});


// Split user skills into pills on all user page
function splitSkills() {
    var skillsLists = $('.user-skills')
    for (i = 0; i < skillsLists.length; i++) {
        var maxSkillsShown = 5;
        var limitReached = false;
        console.log(skillsLists)

        if ($(skillsLists[i]).text() != "") {
            var skillSet = $(skillsLists[i]).text().split(',');
            $(skillsLists[i]).text("");
            skillSet.forEach(function callback(element, index) {
                if (index <= (maxSkillsShown - 1)) {
                    $(skillsLists[i]).append(`
            <span class="skill-pill">${element}</span>
            `);
                } else if (limitReached != true) {
                    var skillsHidden = skillSet.length - maxSkillsShown
                    $(skillsLists[i]).append(`
                    <span class="skill-pill">+${skillsHidden}</span>
                    `);
                    limitReached = true;
                } else {
                    return false;
                }
            })
        }
    }
};
splitSkills();


/* Custom skill pill add and remove, to interact with 
hidden dropdown when user clicks custom button */
function addSkill() {
    $('#skills-select').find('.vscomp-toggle-button').click()
}
function removeSkill(skill) {
    var skill_name = $(skill).attr('value')
    var skillSelect = $(`.vscomp-option[data-value="${skill_name}"]`)
    if ($(skillSelect).hasClass('selected')) {
        skillSelect.click()
        $(this).parent().remove()
    }
}


// Sidebar Nav Expand / Collapse
function triggerSidebar() {
    let sidebar = $('#sidebar_wrap')
    if (sidebar.hasClass('active')) {
        $('#sidebar_wrap').removeClass('active');
        $('.sidebar-profile-details').addClass('closed');
        $('#account_sidebar > ul').addClass('closed')
        $('.sidenav-detail-text').fadeOut('fast');
        $('.sidebar-text-item > span').fadeOut()
        if (screenWidth <= 991.98) {
            $('body').css('overflow-y', 'auto');
        }
    } else {
        $('#sidebar_wrap').addClass('active');
        $('.sidebar-profile-details').removeClass('closed');
        $('#account_sidebar > ul').removeClass('closed');
        $('.sidenav-detail-text').delay('100').fadeIn();
        $('.sidebar-text-item > span').fadeIn('fast')
        if (screenWidth <= 991.98) {
            $('body').css('overflow-y', 'hidden');
        }
    }
};


// Click the hidden file input 
function prfImgUpload() {
    $('#profile_image').click();
}


// Preview image before upload
/* Syntax guidance from Suresh Pattu in this StackOverflow thread - 
   https://stackoverflow.com/questions/18694437/how-to-preview-image-before-uploading-in-jquery/19649483 */

function previewImage(input) {
    var originalImage = $('.prf-img-preview').attr('src');
    if (input.files && input.files[0]) {
        var uploadedImg = input.files[0];
        var image = new FileReader();
        image.onload = function (e) {
            $('.prf-img-preview').attr('src', e.target.result);

            // Create image data to validate input
            var imgFile = new Image();
            imgFile.src = e.target.result;
            imgFile.onload = function () {
                specImageOrientation(imgFile)
                var height = imgFile.height;
                var width = imgFile.width;
                var size = uploadedImg.size;
                if (height > 1000 || width > 1000) {
                    $('.prf-img-preview').attr('src', originalImage);
                    $(`<ul class='errorlist'><li>
                        Your image is too large - please upload an image no larger than
                        1000 x 1000 pixels and 10mb. Select another to upload a new image.
                        </li>
                        </ul>`).insertAfter(input);
                }

            }

        }
        image.readAsDataURL(uploadedImg);
    }
}

$('input#profile_image').on('change', function () {
    previewImage(this)
});


/* All user page - determine whether user header details 
are wrapped and apply 'text-center' class if so */
    $('.user-details-mast').each(function(){
        console.log($(this).width())
        var width = parseInt($(this).width())
        var parent = parseInt($(this).parent().width() -110)
        if (parent <= width){
            $(this).addClass('text-center')
        }
    })


/***
 * AJAX HANDLERS 
 ***/

// Generic get data (to load page template on dashboard) 
function get_ajax_data(url) {
    $.ajax({
        type: 'GET',
        url: url,
        timeout: 10000,
        success: function (data) {
            $('#ajax_content').html(data)
        },
        error: function (data) {
            console.log("There has been an error")
        }
    })
}


// Submit an AJAX search form on 'all users' page
$('#user_search_form').submit(function (e) {
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
            setCtaBtns();
            splitSkills();
        },
        error: function (data) {
            console.log("There has been an error")
        }
    })
});


// Add user as connection
function add_friend(other_user) {
    $.ajax({
        type: 'GET',
        url: `../ajax/add_friend/${other_user}`,
        timeout: 10000,
        success: function (data) {
            console.log("The response: ", data.response);
            changeButtonUI(data.buttonId, data.type);
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
            changeButtonUI(data.buttonId, data.type);
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
            changeButtonUI(data.buttonId, data.type);
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
            changeButtonUI(data.buttonId, data.type);
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
            changeButtonUI(data.buttonId, data.type);
        },
        error: function (data) {
            console.log("There has been an error")
        }
    })
};

// Set friendship buttons on each card on page load
function setCtaBtns() {
    $(`.req-sent-btn`).each(function () {
        var buttonId = $(this).val();
        $(`.send-connection-btn[value="${buttonId}"]`).remove();
    });
    let acceptBtn = $(`.accept-connection-btn`).each(function () {
        var buttonId = $(this).val();
        $(`.send-connection-btn[value="${buttonId}"]`).remove();
    });
}
setCtaBtns();


// Change connection action button on hover, advising to user what clicking button will do
(function changeButtonText() {
    $('.user-cta button').mouseenter(function () {
        if ($(this).hasClass('req-sent-btn')) {
            $(this).html('<i class="fas fa-times px-2"></i>Cancel Request');
        } else if ($(this).hasClass('remove-connection-btn')) {
            $(this).html('<i class="fas fa-exit px-2"></i>Remove Connection');
        }
    });
    $('.user-cta button').mouseleave(function () {
        if ($(this).hasClass('req-sent-btn')) {
            $(this).html('Connection Request Sent');
        } else if ($(this).hasClass('remove-connection-btn')) {
            $(this).html('Connected');
        }
    })
})();


// Change the friend 'connection' button on successful add
function changeButtonUI(buttonId, type) {
    let buttonTarget = $(`.send-connection-btn[value="${buttonId}"]`);
    $(buttonTarget).text('Connection Request Sent');
    $(buttonTarget).removeClass('send-connection-btn').addClass('req-sent-btn');
    $(buttonTarget).removeClass('primary-btn').addClass('primary-btn-outline-color');
    $(buttonTarget).attr('onclick', `cancel_friend(${buttonId});`);
    if (type == "cancel") {
        let buttonTarget = $(`.req-sent-btn[value="${buttonId}"]`);
        $(buttonTarget).text('Send Connection Request');
        $(buttonTarget).addClass('send-connection-btn').removeClass('req-sent-btn');
        $(buttonTarget).addClass('primary-btn').removeClass('primary-btn-outline-color');
        $(buttonTarget).attr('onclick', `add_friend(${buttonId});`);
    } else if (type == "remove") {
        $('.send-message-btn').fadeOut();
        let buttonTarget = $(`.remove-connection-btn[value="${buttonId}"]`);
        $(buttonTarget).text('Connection Removed');
        $(buttonTarget).attr('onclick', ``);
    } else if (type == "accept") {
        let buttonTarget = $(`.accept-connection-btn[value="${buttonId}"]`);
        $(buttonTarget).text('Connection Accepted ');
    } else {
        $(`.conn-request-item[value="${buttonId}"]`).fadeOut("fast", "linear");
    }
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
            location.reload()
        },
        error: function (data) {
            console.log("There has been an error")
        }
    })
};