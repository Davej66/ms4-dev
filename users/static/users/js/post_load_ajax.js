// AJAX Handlers



function update_subscription(new_package) {
    let url = ""
    console.log(token)
    $.ajax({
        type: 'POST',
        url: "/checkout/update_subscription",
        dataType: "json",
        data: JSON.stringify({
            "csrfmiddlewaretoken": csrftoken,
            "new_package": new_package
        }),
        timeout: 10000,
        success: function (data) {
            data.preventDefault();
            console.log(data)
        },
        error: function (data) {
            console.log("There has been an error", token2)
        }
    })
    }