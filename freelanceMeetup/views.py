from django.shortcuts import redirect, render


def err_404(request, *args, **kwargs):
    """ Render 404 Page """
    return render(request, 'errors/err_404.html', status=404)


def err_500(request, *args, **kwargs):
    """ Render 500 Page """
    return render(request, 'errors/err_500.html', status=500)