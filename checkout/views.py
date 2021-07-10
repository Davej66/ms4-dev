from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib import messages
from .contexts import order_summary_context
from .forms import OrderForm
from users.forms import UpdateUserPackage
from users.models import MyAccount
from packages.models import Package

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
    user_email = request.user
    user = MyAccount.objects.get(email=user_email)
    name = user.first_name + " " + user.last_name

    package_selection = request.session['package_selection']['package_id']
    current_package = Package.objects.get(pk=package_selection)

    if not stripe_pk:
        messages.warning(request, "No public key found for Stripe")

    if request.method == 'POST':
        total_cost = current_package.price
        stripe_total = round(total_cost * 100)
        form_data = {
            "buyer_name": name.title(),
            "buyer_email": user_email,
            "package_purchased": current_package,
            "order_total": total_cost,
        }
        profile_form_data = {
            "package_tier": current_package.tier,
            "package_name": current_package
        }
        order_form = OrderForm(form_data)
        profile_form = UpdateUserPackage(profile_form_data, instance=request.user)
        print("valid:", profile_form.errors)
        if order_form.is_valid() and profile_form.is_valid():
            order_form.save()
            profile_form.save()
        return redirect(order_confirmation)
    
    else:
        total_cost = current_package.price
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
        
        return render(request, 'checkout/order_summary.html', context)

    return render(request, 'checkout/checkout.html')


def checkout(request):
    return render(request, 'checkout/checkout.html')


def order_confirmation(request):
    return render(request, 'checkout/order_confirmation.html')