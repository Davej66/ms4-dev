/* Append allauth form errors to input parent 
in order to style relative to invalid input */

$(document).ready(function () {
    var getErrors = $('.errorlist').each(function (index) {
        error = $(this)
        var invalidInput = error.next()
        error.appendTo(invalidInput)  
    })
})