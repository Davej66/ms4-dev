from django.shortcuts import render, HttpResponse
from django.http import JsonResponse
from django.conf import settings
from django.contrib import messages
from django.template.loader import render_to_string
from users.forms import ProfileForm
from allauth.account.decorators import verified_email_required
from users.models import MyAccount
from django.template.loader import render_to_string

import stripe
import json

@verified_email_required
def account_dashboard(request):

    user = MyAccount.objects.get(email=request.user)
    full_name = user.first_name + " " + user.last_name
    user_package = user.package_name
    print(request.user)
    if request.method == "POST":
        form_data = {
            "first_name": "bradley",
            "last_name": "cooney",
            "job_role": "producer",
        }

        profile_form = ProfileForm(form_data, instance=request.user)
        print(profile_form.errors)
        if profile_form.is_valid():
            profile_form.save()
            print("saved: ", form_data)

    context = {
        'full_name': full_name.title(),
        'package': user_package,
    }

    return render(request, 'users/dashboard.html', context)


""" AJAX REQUESTS """

# Ajax function inspiration from Coding with Mitch tutorials - https://codingwithmitch.com/
@verified_email_required
def dashboard_my_orders(request):

    stripe_sk = settings.STRIPE_SECRET_KEY
    stripe.api_key = stripe_sk

    user = MyAccount.objects.get(email=request.user)
    stripe_customer_id = user.stripe_customer_id
    
    invoices = stripe.Invoice.list(
        limit=10,
        customer = stripe_customer_id)

    context = {
        'invoices': invoices
        }
        
    payload = render_to_string('users/includes/dashboard_orders.html', context)
    return HttpResponse(json.dumps(payload), content_type="application/json")