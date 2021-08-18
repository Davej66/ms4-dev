const csrftoken = Cookies.get('csrftoken');


/* PACKAGE SELECTION */
// Store the package in session on select and move user to confirmation page
function select_package(packageId){
    payload = {
        'csrfmiddlewaretoken': csrftoken,
        'package_id': packageId
    }
    $.ajax({
        type: 'POST',
        datatype: 'json',
        data: payload,
        url: '../checkout/package_select/ajax/store_selection/',
        timeout: 10000,
        success: function (data) {
            window.location.replace('../checkout/confirm_order/')
            console.log("This Worked", data.proceed)
        },
        error: function (data) {
            console.log("There has been an error")
        }
    });
};