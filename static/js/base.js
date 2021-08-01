/* Append allauth form errors to input parent 
in order to style relative to invalid input */

$(document).ready(function () {
    var getErrors = $('.errorlist').each(function (index) {
        error = $(this)
        var invalidInput = error.next()
        error.appendTo(invalidInput)  
    })
})


// Auto resize textarea
function resizeTextarea(textarea) {
    var currentHeight = $(textarea).height();
    var scrollHeight = $(textarea).prop('scrollHeight');
    if ((scrollHeight - 10) > currentHeight) {
        if (scrollHeight > 240) {
            $(textarea).css('overflow-y', 'auto');
        }
        textarea.style.height = scrollHeight + 'px';
    }
}
