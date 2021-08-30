from django.shortcuts import redirect, render
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages


def index(request):
    """ Render Homepage """
    return render(request, 'home/index.html')


def privacy(request):
    """ Render Privacy Page """
    return render(request, 'home/privacy.html')


def contact(request):
    """ Render Contact Page """

    if request.method == "POST":
        
        sender = request.POST.get('email')
        name = request.POST.get('name')
        subject = request.POST.get('subject')
        message = request.POST.get('contact_message')
        to_email = settings.DEFAULT_FROM_EMAIL
        
        send_mail(
            subject, message, sender,
            [to_email],
            reply_to=[to_email],
            fail_silently=False,
        )
        
        messages.success(request, "Your message has been sent to us, we will respond to you within 48 Hours!")
        return redirect('account_dashboard')
        
    return render(request, 'home/contact.html')
