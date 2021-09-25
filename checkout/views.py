from django import http
from django.shortcuts import (
    render, redirect, get_object_or_404)
from django.http import JsonResponse, HttpResponse
from django.template.loader import render_to_string
from django.views.decorators.http import last_modified, require_POST
from django.conf import settings
from django.contrib import messages
from allauth.account.decorators import verified_email_required
from .contexts import order_summary_context
from .forms import OrderForm
from .models import Order
from users.forms import UpdateUserPackage, AddUserSubscription
from users.models import MyAccount
from packages.models import Package
from events.models import Event
from datetime import datetime

import stripe
import json

# Create your views here.


@require_POST
def checkout_cache(request):
    # TODO Extend this out
    pid = request.POST.get('client_secret').split('_secret')[0]
    stripe.api_key = settings.STRIPE_SECRET_KEY
    stripe.Subscription.modify(pid, metadata={
        'email': request.user
    })


def store_selection(request):
    """ Get package selection from packages page and store in session 
        for remainder of checkout process """

    if request.is_ajax() and request.method == "POST":
        # Get the package id from the ajax request

        user_auth = request.user
        user_str = str(user_auth)
        package = request.POST['package_id']
        request.session['package_selection'] = package

        if user_str == 'AnonymousUser':
            send_to_reg = True
            return JsonResponse({'response': "Success", 'registration': True})

        return JsonResponse({'response': "Success", 'proceed': True})

    return JsonResponse({'response': "Something went wrong, please try again",
                         'proceed': False})


def confirm_order(request):
    """ Create the payment method, customer and subscription if none exist and 
        confirm the subscription if payment method successfully provided """

    context = {}

    # Remove all pre-existing messages on page load.
    # Credits: SpiXel in this SO thread: https://stackoverflow.com/questions/39518310/delete-all-django-contrib-messages
    storage = messages.get_messages(request)
    storage.used = True

    stripe_pk = settings.STRIPE_PUBLIC_KEY
    stripe_sk = settings.STRIPE_SECRET_KEY
    stripe.api_key = stripe_sk

    user_email = request.user
    user = MyAccount.objects.get(email=user_email)
    name = user.first_name + " " + user.last_name
    free_package_id = Package.objects.get(tier=1).stripe_price_id

    # Determine if the subscription is an upgrade or new account
    sub_is_change = False

    if not request.session['package_selection']:
        return redirect('packages')
    else:
        package_selection = int(request.session['package_selection'])

    package_item = Package.objects.get(tier=package_selection)
    package_stripe_id = package_item.stripe_price_id
    customer_pm_details = None
    sub_price_id = None
    latest_bill_paid = "open"

    if not stripe_pk:
        messages.warning(request, "No public key found for Stripe")

    # Create a new stripe customer if none exists for this site user
    if not user.stripe_customer_id:
        try:
            customer_str_id = stripe.Customer.create(
                email=user_email,
                name=name
            )

            user.stripe_customer_id = customer_str_id.id
            user.save()
            pass

        except Exception as e:
            error = str(e)
            return error

    # Check for existing stripe sub ID and create if not found
    if not user.stripe_subscription_id and package_item.tier != 1:

        try:
            subscription = stripe.Subscription.create(
                customer=user.stripe_customer_id,
                items=[{
                    'price': package_item.stripe_price_id
                }],
                payment_behavior='default_incomplete',
                expand=['latest_invoice.payment_intent'],
            )

            user.stripe_subscription_id = subscription.id
            user.save()
            pass

        except Exception as e:
            return JsonResponse({'message': e.user_message}), 400
    elif package_item.tier != 1:
        subscription = stripe.Subscription.retrieve(
            user.stripe_subscription_id,
            expand=['latest_invoice.payment_intent'])

        latest_bill_paid = subscription.latest_invoice.status
        sub_price_id = subscription.plan.id
    else:
        subscription = ""
    
    # Update customer default payment method for future changes
    customer_has_pm = stripe.Customer.retrieve(
        user.stripe_customer_id
    )
    

    try:
        sub_payment_method = subscription.latest_invoice.payment_intent.charges.data[0].payment_method
    except:
        sub_payment_method = None

    
    if customer_has_pm.invoice_settings.default_payment_method == None:
        print("No payment method")
        stripe.Customer.modify(
            user.stripe_customer_id,
            invoice_settings={'default_payment_method': sub_payment_method}
        )
    else:
        customer_pm = stripe.PaymentMethod.retrieve(
            customer_has_pm.invoice_settings.default_payment_method
        )

        customer_pm_details = {
            "brand": customer_pm.card.brand,
            "last4": customer_pm.card.last4,
            "exp_m": customer_pm.card.exp_month,
            "exp_y": customer_pm.card.exp_year,
        }
        context['customer_pm_details'] = customer_pm_details
    
        
    if request.method == 'POST':

        # If user updates their details on form, update their account
        user.package_tier = package_item.tier
        user.package_name = package_item.name
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.email = request.POST.get('email', user.email)
        user.save()

        # Update the stripe customer with name and email
        stripe.Customer.modify(
            user.stripe_customer_id,
            email=user.email,
            name=user.first_name + " " + user.last_name,
        )

        # Check if updated sub based on new package required and update if yes
        subscription = stripe.Subscription.retrieve(
            user.stripe_subscription_id)
        stripe.Subscription.modify(
            subscription.id,
            cancel_at_period_end=False,
            proration_behavior='none',
            items=[{
                'id': subscription['items']['data'][0].id,
                'price': package_item.stripe_price_id,
            }]
        )
    
        
        new_payment_method = request.POST.get('payment_method')

        stripe.Customer.modify(
            user.stripe_customer_id,
            invoice_settings={'default_payment_method':
                              new_payment_method}
        )

        request.session['package_selection'] = ""
        storage = messages.get_messages(request)
        storage.used = True
        messages.success(request, "You have successfully subscribed!")
        return redirect('get_my_orders')

    # Send end of current period to context
    if subscription != "" and subscription.plan.id is not free_package_id:

        upcoming_inv = stripe.Invoice.upcoming(
            customer=user.stripe_customer_id,
        )
        next_period_start = datetime.fromtimestamp(upcoming_inv.next_payment_attempt).strftime(
            '%d %b %y')
        current_end = datetime.fromtimestamp(subscription.current_period_end).strftime(
            '%d %b %y')
        stripe_client_secret = subscription.latest_invoice.payment_intent
    elif subscription != "":
        next_period_start = ""
        current_end = datetime.fromtimestamp(subscription.current_period_end).strftime(
            '%d %b %y')
    else:
        next_period_start = ""
        current_end = ""
        stripe_client_secret = ""

    # If user attempting to purchase the same subscription, send them to their orders
    if sub_price_id == package_stripe_id and latest_bill_paid == "paid":
        messages.error(request, "You are already subscribed to this package!")
        return redirect('get_my_orders')
    elif latest_bill_paid == 'paid' and customer_has_pm.invoice_settings.default_payment_method:
        print("upgrade")
        sub_is_change = True
    elif customer_has_pm.invoice_settings.default_payment_method and package_selection == 1:
        # User is downgrading to free account
        sub_is_change = True
    else:
        sub_is_change = False

    if customer_pm_details is None:
        customer_pm_details = ""
    
    
    
    print("stripe_client_secret", subscription)
    
    if stripe_client_secret != "":
            stripe_client_secret = subscription.latest_invoice.payment_intent.client_secret
    else: 
        stripe_client_secret = None
    
    context = {
        "stripe_public_key": stripe_pk,
        # 'subId': subscription.id or None,
        'stripe_client_secret': stripe_client_secret,
        'package_selected': package_item,
        'upgrade': sub_is_change,
        'next_period_start': next_period_start,
        'current_period_end': current_end,
        'customer_pm_details': customer_pm_details
    }

    return render(request, 'checkout/confirm_order.html', context)


def cancel_abandoned_subscription(request):
    """ Call this function when user leaves page to destroy the subscription created """

    stripe_pk = settings.STRIPE_PUBLIC_KEY
    stripe_sk = settings.STRIPE_SECRET_KEY
    stripe.api_key = stripe_sk

    user = request.user

    subscription = stripe.Subscription.retrieve(
        user.stripe_subscription_id
    )

    latest_invoice = stripe.Invoice.retrieve(
        subscription.latest_invoice
    )

    if subscription and latest_invoice.status == 'open':
        stripe.Customer.delete(
            user.stripe_customer_id
        )

        user.stripe_subscription_id = ""
        user.stripe_customer_id = ""
        user.save()

    return HttpResponse(content="Subscription has been removed", status=200)


def update_payment_method(request):
    """ Update the default payment method of user if required """
    stripe_sk = settings.STRIPE_SECRET_KEY
    stripe.api_key = stripe_sk
    stripe_customer = request.user.stripe_customer_id

    if request.method == "POST":
        new_payment_method = request.POST.get('payment_method')

        stripe.PaymentMethod.attach(
            new_payment_method,
            customer=stripe_customer,
        )

        stripe.Customer.modify(
            stripe_customer,
            invoice_settings={'default_payment_method':
                              new_payment_method}
        )

        messages.success(
            request, 'Your payment card has been added, we will attempt to bill this card shortly.')

    return redirect('get_my_orders')
