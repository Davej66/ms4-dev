// Initialize on page load

// Get all skills and roles on page if they exist and return variables if yes
const getSkills = document.getElementById('all_skills')
const skills = getSkills ? JSON.parse(document.getElementById('all_skills').textContent) : "";
const getUserSkills = document.getElementById('user_skills')
const userSkills = getUserSkills ? JSON.parse(document.getElementById('user_skills').textContent) : "";
const getUserInd = document.getElementById('user_ind')
const userInd = getUserInd ? JSON.parse(document.getElementById('user_ind').textContent) : "";
const getRoles = document.getElementById('all_roles')
const roles = getUserInd ? JSON.parse(document.getElementById('all_roles').textContent) : "";
const getUserRole = document.getElementById('user_role')
const userRole = getUserRole ? JSON.parse(document.getElementById('user_role').textContent) : "";
const screenWidth = $(window).width()

$(document).ready(function () {
    // Check screen width and remove active from sidenav if mobile
    if(screenWidth > 991.98){
        $('#sidebar_wrap').addClass('active')
    }

    /** 
    * Multiselect library by 'sa-si-dev': https://sa-si-dev.github.io/virtual-select/
    **/

    // Skill Select
    (function () {
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
        var userSkillsArr = userSkills.split(',');

        // Add existing skills to display
        for (i = 0; i < vsOptions.length; i++) {
            var skill = vsOptions[i]
            var skill_name = $(skill).attr('data-value')
            if (userSkillsArr.includes(skill_name)) {
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

    // Industry Select - options from below, not from DB
    (function () {
        var industry = VirtualSelect.init({
            ele: '#ind_select_profile_edit',
            selectedValue: userInd,
            hideClearButton: true,
            options: [{
                'label': 'Photography',
                'value': 'Photography',
            },
            {
                'label': 'Events Management',
                'value': 'Events Management',
            },
            {
                'label': 'Music',
                'value': 'Music',
            },
            {
                'label': 'Film & TV',
                'value': 'Film & TV',
            },
            {
                'label': 'Theatre',
                'value': 'Theatre',
            },
            ],
            multiple: false,
            name: 'industry',
            additionalClasses: 'select-edit-profile'
        });


    })();

    // Job Role Select - options from DB
    (function () {
        var role = VirtualSelect.init({
            ele: '#role_select_profile_edit',
            hideClearButton: true,
            options: [],
            multiple: false,
            name: 'job_role',
            search: true,
            additionalClasses: 'select-edit-profile',
            selectedValue: userRole,
        })
        for (i = 0; i < roles.length; i++) {
            document.querySelector('#role_select_profile_edit').addOption({
                value: roles[i],
                label: roles[i],
            });
        };
        let roleWrap = $('#role_select_profile_edit')
        $(roleWrap).find(`div[data-value='${userRole}']`).addClass('selected');
        $(roleWrap).find(`input[name='job_role']`).val(`${userRole}`);
        $(roleWrap).find(`.vscomp-value`).text(`${userRole}`);
    })();


    /** 
    * Open select boxes and allow selection using keyboard only
    **/

    // Give all select options tabindex
    $('.vscomp-option').each(function (item) {
        $(this).attr('tabindex', '0');
    });

    // Remove tabindex from hidden fields
    $('.vscomp-hidden-input').attr('tabindex', '-1')

    let toggleInd = $('#ind_select_profile_edit')
    let toggleRole = $('#role_select_profile_edit')

    function openSelectOnTab(select) {
        $(select).keyup(function (e) {
            var key = e.keycode || e.which
            if (key == 9 || key == 13 || key == 32) {
                $(select).find('.vscomp-toggle-button').click();
                $(select).find('.vscomp-option').first().focus().toggleClass('focused');
            }
        });
    }
    openSelectOnTab(toggleInd);
    openSelectOnTab(toggleRole);
});


// Split user skills into pills on all user page
function splitSkills() {
    var skillsLists = $('.user-skills')
    for (i = 0; i < skillsLists.length; i++) {
        if ($(skillsLists[i]).text() != "") {
            var skillSet = $(skillsLists[i]).text().split(',');
            $(skillsLists[i]).text("");
            skillSet.forEach(element => {
                $(skillsLists[i]).append(`
            <span class="skill-pill">${element}</span>
            `)
            })
        }
    }
};
splitSkills();

/* Custom skill pill add and remove, to interact with 
hidden dropdown when user clicks custom button */
function addSkill(toggle) {
    $('#skills-select').find('.vscomp-toggle-button').click()
}
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
    let sidebar = $('#sidebar_wrap')
    if (sidebar.hasClass('active')) {
        $('#sidebar_wrap').removeClass('active');
        $('.sidebar-profile-details').addClass('closed');
        $('#account_sidebar > ul').addClass('closed');
        $('.sidenav-detail-text').fadeOut(200);
        $('.sidebar-text-item').fadeOut(200);
        if (screenWidth <= 991.98) {
            $('body').css('overflow-y', 'auto');
        }
    } else {
        $('#sidebar_wrap').addClass('active');
        $('.sidebar-profile-details').removeClass('closed');
        $('#account_sidebar > ul').removeClass('closed');
        $('.sidenav-detail-text').delay('100').fadeIn();
        $('.sidebar-text-item').delay('500').fadeIn();
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
                console.log(height, width)
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
            $('#search_results').html(data)
            console.log('this worked', data)

        },
        error: function (data) {
            console.log("There has been an error")
        },
        complete: function (data) {
            console.log("Complete")
        }
    })
});