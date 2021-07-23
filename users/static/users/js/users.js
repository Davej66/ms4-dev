// Sidebar Nav Expand / Collapse

function triggerSidebar(){
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

// AJAX Handlers

function get_ajax_data(url){
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
