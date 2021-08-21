from django.shortcuts import render


def index(request):
    """ Render Homepage """
    return render(request, 'home/index.html')


def privacy(request):
    """ Render Privacy Page """
    return render(request, 'home/privacy.html')


def contact(request):
    """ Render Contact Page """
    return render(request, 'home/contact.html')
