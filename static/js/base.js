// Add 'scrolled' to navbar
$(document).scroll(function () {
    if ($(document).scrollTop() >= 50) {
        $('.navbar').addClass('scrolled');
    } else {
        $('.navbar').removeClass('scrolled');
    }
});


$(document).ready(function () {

    var dropdownId = $('.dropdown-toggle').attr('id');
    var dropdownMenu = $(`ul[aria-labelledby=${dropdownId}]`);
    var messages = $('.message-wrap')

    // Hide messages after 10 seconds
    setTimeout(() => {
        $(messages).fadeOut();
    }, 10000);

    // Determine which navbar to show
    var titleArr = ['Home | FreelanceMeetups', 'Register | FreelanceMeetups',
        'Login | FreelanceMeetups']
    var title = document.title;
    var titleShort = title.split('|')[0].trim();
    console.log(title)
    var titleConfirmed = titleArr.includes(title);
    if (titleConfirmed == true) {
        $('.navbar').addClass('transparent-nav');
    } else {
        $('.navbar').removeClass('transparent-nav');
    }

    // Add 'active' class to current page nav link
    var currPath = window.location.pathname;
    var currPageNavLink = $(`.nav-link[href="${currPath}"`);
    var isCtaLink = $(currPageNavLink).hasClass('no-active-highlight');
    if (isCtaLink == false) {
        $(currPageNavLink).addClass('active');
    }


    // Open navbar dropdown on hover
    $('.dropdown-toggle').hover(
        function () {
            $(dropdownMenu).addClass('show');
            $(dropdownMenu).addClass('fade-in');
        },
        function () {
            $(dropdownMenu).removeClass('show');
            $(dropdownMenu).removeClass('fade-in');
        }
    );

    $(dropdownMenu).hover(
        function () {
            $(dropdownMenu).addClass('show');
        },
        function () {
            $(dropdownMenu).removeClass('show');
        }
    );

    var getErrors = $('.errorlist').each(function (index) {
        error = $(this);
        var invalidInput = error.next();
        error.appendTo(invalidInput);
    });

    // Switch navbar-toggler to cross when selected
    $('.navbar-toggler').click(function () {
        var open = $('.navbar-toggler > i').hasClass('fa-bars');
        var toggler = $(this).children()
        if (open == true) {
            $(toggler).removeClass('fa-bars')
            $(toggler).addClass('fade-in')
            $(toggler).addClass('fa-times')
        } else {
            $(toggler).removeClass('fa-times')
            $(toggler).removeClass('fade-in')
            $(toggler).addClass('fa-bars')
        }
    })
});


// Auto resize textarea
function resizeTextarea(textarea) {
    var currentHeight = $(textarea).height();
    var scrollHeight = $(textarea).prop('scrollHeight');
    if (scrollHeight > currentHeight) {
        if (scrollHeight > 240) {
            $(textarea).css('overflow-y', 'auto');
        }
        $(textarea).animate({
            height: scrollHeight
        }, 100);
    }
}


// Specify profile image rotation and add appropriate class
function specImageOrientation(image) {
    var height = image.height;
    var width = image.width;
    if (height > width) {
        $(image).removeClass('landscape-img');
        $(image).addClass('portrait-img');
    } else if (height < width) {
        $(image).removeClass('portrait-img');
        $(image).addClass('landscape-img');
    } else {
        $(image).addClass('square-img');
    }
}


// Remove message when 'times' clicked
function removeMessage(closeMessage) {
    let message = $(closeMessage).parent();
    $(message).animate({
        top: '-30%',
    }, 200);
}


// Show verify form submission options
function verifyForm(firstButton) {
    $('.form-submit-verify').css('display', 'flex').animate(
        {
            opacity: '1',
            width: '50%'
        }, 100);
    if ($(firstButton).hasClass('verify')) {
        $(firstButton).attr('type', 'submit');
    } else {
        $(firstButton).addClass('verify').text('I know! Update Information');
        $(firstButton).animate({
            width: '50%'
        }, 100);
    }
}



