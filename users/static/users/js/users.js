// Initialize on page load
const skills = JSON.parse(document.getElementById('all_skills').textContent);

$(document).ready(function () {

    (function () {
        // Multiselect library by 'sa-si-dev': https://sa-si-dev.github.io/virtual-select/
        VirtualSelect.init({
            ele: '#skills-select',
            options: [],
            multiple: true,
            name: 'skills',

        });
        for (i = 0; i < skills.length; i++) {
            document.querySelector('#skills-select').addOption({
                value: skills[i],
                label: skills[i],
            });
        };

        var vsOptions = $('.vscomp-options > .vscomp-option');
        var skillsDisplay = $('#skills_display');
        var userSkills = ['HTML', 'CSS'];

        // Add existing skills to display
        for (i = 0; i < vsOptions.length; i++) {
            var skill = vsOptions[i]
            var skill_name = $(skill).attr('data-value')
            if (userSkills.includes(skill_name)) {
                $(skill).click()
                skillsDisplay.append(`
                <span class="skill-pill" value="${skill_name}">${skill_name}
                <i class="fas fa-times" value="${skill_name}" onclick="removeSkill(this);"></i>
                </span>
                `)
            }
        }

        // Add or remove skills on input select
        vsOptions.click(function () {
            var skill_name = $(this).text().trim()
            if ($(this).hasClass('selected')) {
                $(`.skill-pill[value="${skill_name}"]`).remove()
            } else {
                skillsDisplay.append(`
                <span class="skill-pill" value="${skill_name}">${skill_name}
                <i class="fas fa-times" value="${skill_name}" onclick="removeSkill(this);"></i>
                </span>
                `)
            }
        })
    })();
});
    function removeSkill(skill) {
        var skillPillClose = $('#skills_display > .skill-pill');
            var skill_name = $(skill).attr('value')
            var skillSelect = $(`.vscomp-option[data-value="${skill_name}"]`)
            if ($(skillSelect).hasClass('selected')) {
                skillSelect.click()
                $(this).parent().remove()
            }
    }



// Sidebar Nav Expand / Collapse
function triggerSidebar() {
    sidebar = $('#sidebar_wrap')
    console.log(sidebar)
    if (sidebar.hasClass('active')) {
        $('#sidebar_wrap').removeClass('active')
        $('.sidebar-profile-details').addClass('closed')
        $('#account_sidebar > ul').addClass('closed')
        $('.sidenav-detail-text').fadeOut(200);
        $('.sidebar-text-item').fadeOut(200);
    } else {
        $('#sidebar_wrap').addClass('active')
        $('.sidebar-profile-details').removeClass('closed')
        $('#account_sidebar > ul').removeClass('closed')
        $('.sidenav-detail-text').delay('100').fadeIn();
        $('.sidebar-text-item').delay('500').fadeIn();
    }
};

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


// Click the hidden file input 
function prfImgUpload() {
    $('#profile_image').click();
}


// Preview image before upload
/* Syntax guidance from Suresh Pattu in this StackOverflow thread - 
   https://stackoverflow.com/questions/18694437/how-to-preview-image-before-uploading-in-jquery/19649483 */

function previewImage(input) {
    var originalImage = $('.prf-img-preview').attr('src');
    console.log(originalImage)
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
                if (height > 1000 || width > 1000 || size > 1024) {
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
})

// AJAX Handlers

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
