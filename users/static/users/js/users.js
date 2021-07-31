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
    } else if(height < width) {
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
                if (height > 500 || width > 500 || size > 1024) {
                    $(`<ul class='errorlist'><li>
                        Your image is too large - please upload an image no larger than
                        500 x 500 pixels and 10mb. Select another to upload a new image.
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
