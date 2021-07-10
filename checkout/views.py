from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib import messages
from .contexts import order_summary_context
from .forms import OrderForm

import stripe

# Create your views here.

def package_selection(request, package_id):

    context = {}
    package_selection = request.session.get('package_selection', {})

    package_selection['package_id'] = package_id
    request.session['package_selection'] = package_selection
    
    context['p_selected'] = request.session
    print(context['p_selected'], "session: ", request.session['package_selection'])

    return redirect(order_summary)


def order_summary(request):
    
    stripe_pk = settings.STRIPE_PUBLIC_KEY
    stripe_sk = settings.STRIPE_SECRET_KEY
    username = request.user

    print("user ",username)
    if not stripe_pk:
        messages.warning(request, "No public key found for Stripe")

    if request.method == 'POST':
        current_package = order_summary_context(request)
        total_cost = current_package['package_cost']
        stripe_total = round(total_cost * 100)
        form_data = {
            "buyer_name": username,
            "buyer_email": "admin@admin.com",
            "order_total": total_cost,
        }
        order_form = OrderForm(form_data)
        print("valid:", order_form.errors)
        if order_form.is_valid():
            order_form.save()
        return redirect(order_confirmation)
        
    else: 
        current_package = order_summary_context(request)
        total_cost = current_package['package_cost']
        stripe_total = round(total_cost * 100)
        stripe.api_key = stripe_sk
        intent = stripe.PaymentIntent.create(
            amount=stripe_total,
            currency = settings.STRIPE_CURRENCY,
        )
        context = {
            "stripe_public_key": stripe_pk,
            "stripe_client_secret": intent.client_secret
        }
        print("price ", intent)
        return render(request, 'checkout/order_summary.html', context)

    return render(request, 'checkout/checkout.html')


def checkout(request):
    return render(request, 'checkout/checkout.html')


def order_confirmation(request):
    return render(request, 'checkout/order_confirmation.html')