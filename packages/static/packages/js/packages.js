const csrftoken = Cookies.get('csrftoken');
var account_required = $('#id_account_required').text();


/* PACKAGE SELECTION */
// Store the package in session on select and move user to confirmation page
function select_package(packageId) {

    if (account_required == "true") {
        var registerModal = new bootstrap.Modal(
            document.getElementById('must_register'), {
            keyboard: false
        })
        registerModal.show()
    } else {
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
                if (data.registration != true) {
                    window.location.replace('../checkout/confirm_order/')
                } else {
                    window.location.replace('../checkout/account_required/')
                }
            },
            error: function (data) {
                console.log("There has been an error")
            }
        });
    }
};