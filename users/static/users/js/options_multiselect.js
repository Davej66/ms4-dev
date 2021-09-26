// Get all skills and roles on page if they exist and return variables if yes
let getSkills = document.getElementById('all_skills')
let skills = getSkills ? JSON.parse(document.getElementById('all_skills').textContent) : "";
let getUserSkills = document.getElementById('user_skills')
let userSkills = getUserSkills ? JSON.parse(document.getElementById('user_skills').textContent) : "";
let getUserInd = document.getElementById('user_ind')
let userInd = getUserInd ? JSON.parse(document.getElementById('user_ind').textContent) : "";
let getRoles = document.getElementById('all_roles')
let roles = getRoles ? JSON.parse(document.getElementById('all_roles').textContent) : "";
let getUserRole = document.getElementById('user_role')
let userRole = getUserRole ? JSON.parse(document.getElementById('user_role').textContent) : "";
let getAccount = document.getElementById('free_account')
let freeAccount = getAccount ? JSON.parse(document.getElementById('free_account').textContent) : "";
let prfComplete = document.getElementById('profile_complete');
let isPrfComplete = prfComplete ? JSON.parse(document.getElementById('profile_complete').textContent) : "";
let skillsDisplay = $('#skills_display');

/* Init on page load */
$(document).ready(function () {
    /** 
    * Multiselect library by 'sa-si-dev': https://sa-si-dev.github.io/virtual-select/
    **/

    // Skill Select
    (function () {
        var userSkillsArr = userSkills.split(',');
        let skillOptions = [];
        for (i = 0; i < skills.length; i++) {
            skillOptions.push({
                value: skills[i],
                label: skills[i],
            });
        }
        VirtualSelect.init({
            ele: '#skills-select',
            options: skillOptions,
            multiple: true,
            name: 'skills',
            search: true,
            maxValues: 0,
            optionsCount: 25,
            selectedValue: userSkillsArr
        });

        // Add existing skills to display
        for (i = 0; i < userSkillsArr.length; i++) {
            var skill = userSkillsArr[i];
            skillsDisplay.append(`
                <span class="skill-pill" value="${skill}">
                    ${skill}
                    <i class="fas fa-times" value="${skill}" onclick="removeSkill(this);"></i>
                </span>
                `);
        }

        /** 
        * Open select boxes and allow selection using keyboard only
        **/

        // Add or remove skills on input select
        // Add new skills to input as user selects
        function addSkillClick() {
            $('#skills-select .vscomp-option').on('click', function () {
                var thisSkill = $(this).text().trim();
                var thisSkillPill = $(`.skill-pill[value="${thisSkill}"]`);
                var isSelected = $(this).hasClass('selected');
                if (thisSkillPill.length == 1) {
                    $(thisSkillPill).fadeOut(300,
                        function () { $(this).remove(); });
                } else {
                    skillsDisplay.append(`
        <span class="skill-pill fade-in" value="${thisSkill}">
        ${thisSkill}
        <i class="fas fa-times" value="${thisSkill}" onclick="removeSkill(this);"></i>
        </span>
        `);
                }
            });
        }
        function addSkillEnter() {
            $('#skills-select .vscomp-option').keyup(function (e) {
                e.stopPropagation();
                e.stopImmediatePropagation();
                var key = e.keycode || e.which;
                if (key == 13) {
                    let focusedOption = $('.vscomp-options').find('.focused').text().trim();
                    var thisSkillPill = $(`.skill-pill[value="${focusedOption}"]`);
                    if (thisSkillPill.length == 1) {
                        $(thisSkillPill).fadeOut(300,
                            function () { $(this).remove(); });
                    } else {
                        skillsDisplay.append(`
        <span class="skill-pill fade-in" value="${focusedOption}">
        ${focusedOption}
        <i class="fas fa-times" value="${focusedOption}" onclick="removeSkill(this);"></i>
        </span>
        `);
                    }
                }
            });
        }
        addSkillClick();
        addSkillEnter();

        // Allow for option selects after scroll or when search function used
        $('.vscomp-options-container').on('scroll', function (e) {
            e.stopPropagation();
            e.stopImmediatePropagation();
            addSkillClick();
            addSkillEnter();
        });
        $('.vscomp-options-container').keyup(function (e) {
            e.stopPropagation();
            e.stopImmediatePropagation();
            var key = e.keycode || e.which;
            if (key == 38 || key == 40) {
                addSkillClick();
                addSkillEnter();
            }
        });
        $('.vscomp-search-input').on('change', function (e) {
            e.stopPropagation();
            e.stopImmediatePropagation();
            addSkillClick();
            addSkillEnter();
        });
    })();


    // Industry Select - options from below, not from DB
    (function () {
        if (freeAccount && isPrfComplete) {
            $('#ind_select_profile_edit').replaceWith(`
            <input type="text" disabled style="pointer-events:none; background: transparent;" value="${userInd}">
            </input>`);
            $('#industry_search').addClass('tooltip-parent').append(`
                <span class="tooltip-top">Upgrade your account to view other industries!</span>
            `);
            $('.fieldset.industry').addClass('tooltip-parent').append(`
                <span class="tooltip-top">Upgrade your account to view other industries!</span>
            `);
        } else {
            var industry = VirtualSelect.init({
                ele: '#ind_select_profile_edit',
                selectedValue: userInd,
                hideClearButton: true,
                options: [
                    {
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
        }
    })();


    /* Add required attr to industry field (JS used to avoid conflict with search functions 
    if set in options_multiselect.js)*/
    (() => {
        var industry_field = $('.ind_field_required > div > input.vscomp-hidden-input')
        $(industry_field).attr('required', true)
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
        });
        for (i = 0; i < roles.length; i++) {
            document.querySelector('#role_select_profile_edit').addOption({
                value: roles[i],
                label: roles[i],
            });
        }
        let roleWrap = $('#role_select_profile_edit');
        $(roleWrap).find(`div[data-value='${userRole}']`).addClass('selected');
        $(roleWrap).find(`input[name='job_role']`).val(`${userRole}`);
        $(roleWrap).find(`.vscomp-value`).text(`${userRole}`);
    })();


    // Give all select options tabindex
    $('.vscomp-option').each(function (item) {
        $(this).attr('tabindex', '0');
    });

    // Remove tabindex from hidden fields
    $('.vscomp-hidden-input').attr('tabindex', '-1');

    let toggleInd = $('#ind_select_profile_edit');
    let toggleRole = $('#role_select_profile_edit');

    function openSelectOnTab(select) {
        $(select).keyup(function (e) {
            var key = e.keycode || e.which;
            if (key == 9 || key == 13 || key == 32) {
                $(select).find('.vscomp-toggle-button').click();
                $(select).find('.vscomp-option').first().focus().toggleClass('focused');
            }
        });
    }
    openSelectOnTab(toggleInd);
    openSelectOnTab(toggleRole);
});
