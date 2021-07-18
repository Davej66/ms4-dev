// Sidebar Nav Expand / Collapse

function triggerSidebar(){
        sidebar = $('#sidebar_wrap')
        console.log(sidebar)
        if (sidebar.hasClass('active')) {
            $('#sidebar_wrap').removeClass('active')
            $('#account_sidebar > ul').addClass('closed')
            $('.sidebar-text-item').fadeOut(200);
        } else {
            $('#sidebar_wrap').addClass('active')
            $('#account_sidebar > ul').removeClass('closed')
            $('.sidebar-text-item').delay('500').fadeIn();
        }
};