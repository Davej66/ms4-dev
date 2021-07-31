from django.shortcuts import render, HttpResponse
from django.http import JsonResponse
from django.conf import settings
from django.contrib import messages
from django.template.loader import render_to_string
from allauth.account.decorators import verified_email_required
from allauth.account.views import SignupView
from allauth.account.utils import send_email_confirmation
from users.forms import RegistrationForm, EditProfileForm
from packages.models import Package
from users.models import MyAccount
from django.template.loader import render_to_string
from datetime import datetime

import stripe
import json

# Create customised context for Allauth registration. Credits to Mikeec3
# In this StackOverflow thread: https://stackoverflow.com/questions/29499449/django-allauth-login-signup-form-on-homepage 
class CustomRegistrationView(SignupView):
    
    # Get the original signup form and add the custom form to this
    def get_context_data(self, **kwargs):
        context = super(CustomRegistrationView, self).get_context_data(**kwargs)
        context['reg_form'] = RegistrationForm()
        return context

register = CustomRegistrationView.as_view()

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


@verified_email_required
def edit_profile(request):

    if request.method == 'POST':
        form = EditProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            print("It saved this", form)
            messages.success(request, "Form saved")
        else:
            print("Couldn't save", form.errors)
            messages.error(request, "Form saved")

    return render(request, 'users/edit_profile.html')


@verified_email_required
def view_profile(request, *args, **kwargs):

    view_user = kwargs.get('username')

    context = {
        "user": view_user
    }

    return render(request, 'view_profile.html', context)


""" AJAX REQUESTS """

# Ajax function inspiration from Coding with Mitch tutorials - https://codingwithmitch.com/
@verified_email_required
def dashboard_my_orders(request):

    stripe_sk = settings.STRIPE_SECRET_KEY
    stripe.api_key = stripe_sk

    user = MyAccount.objects.get(email=request.user)
    stripe_customer_id = user.stripe_customer_id
    
    invoices = stripe.Invoice.list(
        limit=3,
        customer = stripe_customer_id)

    upcoming_invoice = stripe.Invoice.upcoming(
        customer = stripe_customer_id,
        )
    
    up_inv_period = upcoming_invoice.lines.data[0].period
    package_id = upcoming_invoice.lines.data[0].price.id
    get_package_object = Package.objects.get(stripe_price_id=package_id)

    upcoming_invoice_dict = {
        "date": datetime.fromtimestamp(
            upcoming_invoice.created).strftime('%d %b %Y'),
        "balance": upcoming_invoice.amount_due / 100,
        "period_start": datetime.fromtimestamp(up_inv_period.start).strftime(
            '%d %b %Y'),
        "period_end": datetime.fromtimestamp(up_inv_period.end).strftime(
            '%d %b %Y'),
        "package": get_package_object
    }


    invoice_list = []

    for i in invoices:
        period = i.lines.data[0].period
        invoice_date = datetime.fromtimestamp(i.created).strftime(
            '%d %b %Y')
        start_date = datetime.fromtimestamp(period.start).strftime(
            '%d %b')
        end_date = datetime.fromtimestamp(period.end).strftime(
            '%d %b %Y')
        invoice_data = {
            "invoice_date": invoice_date,
            "date_start": start_date,
            "date_end": end_date,
            "amount": i.total / 100,
            "download_url": i.invoice_pdf
        }
        invoice_list.append(invoice_data)

    context = {
        'invoices': invoice_list,
        'upcoming_invoice': upcoming_invoice_dict
        }



    payload = render_to_string('users/includes/dashboard_orders.html', context)
    return HttpResponse(json.dumps(payload), content_type="application/json")