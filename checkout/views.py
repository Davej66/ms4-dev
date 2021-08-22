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
from dateutil.relativedelta import relativedelta

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
        print(user_str, type(user_auth))

        if user_str == 'AnonymousUser':
            send_to_reg = True
            return JsonResponse({'response': "Success", 'registration': True})

        return JsonResponse({'response': "Success", 'proceed': True})

    return JsonResponse({'response': "Something went wrong, please try again",
                         'proceed': False})


# TODO - DO WE NEED THIS FUNCTION
# def package_selection(request, package_id, **kwargs):

#     stripe_pk = settings.STRIPE_PUBLIC_KEY
#     stripe_sk = settings.STRIPE_SECRET_KEY
#     stripe.api_key = stripe_sk

#     context = {}
#     user_email = request.user
#     # package_selection = request.session.get('package_selection', {})
#     package_id = kwargs.get('package_id')
#     print(package_id)

#     # package_selection['package_id'] = package_id
#     package_object = Package.objects.get(pk=package_id)
#     request.session['package_selection'] = package_id
#     context['p_selected'] = request.session

#     current_user = MyAccount.objects.get(email=user_email)
#     user_stripe_cus_id = current_user.stripe_customer_id
#     print("I am a stripe user", user_stripe_cus_id)

#     if user_stripe_cus_id is None:
#         try:
#             # Create a new customer object
#             customer = stripe.Customer.create(
#                 email=user_email
#             )
#             package_selection['stripe_cus'] = customer.id
#             package_selection['stripe_price_id'] = package_object.stripe_price_id
#             return redirect(order_summary)

#         except Exception as e:
#             error = str(e)
#             print("error", e)
#             return error
#     else:
#         try:
#             package_selection['stripe_cus'] = user_stripe_cus_id
#             package_selection['stripe_price_id'] = package_object.stripe_price_id
#             return redirect(order_summary)

#         except Exception as e:
#             error = str(e)
#             print("error", e)
#             return error

#     print(context['p_selected'], "session: ",
#           request.session['package_selection'])

#     return redirect(order_summary)


def confirm_order(request):

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

    package_selection = int(request.session['package_selection'])
    package_item = Package.objects.get(tier=package_selection)
    package_stripe_id = package_item.stripe_price_id
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
            print("error", e)
            return error

    # Check for existing stripe sub ID and create if not found
    if not user.stripe_subscription_id:

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
    else:
        subscription = stripe.Subscription.retrieve(
            user.stripe_subscription_id,
            expand=['latest_invoice.payment_intent'])

        latest_bill_paid = subscription.latest_invoice.status
        sub_price_id = subscription.plan.id
    
    
    # Update customer default payment method for future changes
    customer_has_pm = stripe.Customer.retrieve(
            user.stripe_customer_id
        )

    if not customer_has_pm.invoice_settings.default_payment_method:
            stripe.Customer.modify(
                user.stripe_customer_id,
                invoice_settings={'default_payment_method': 
                    subscription.latest_invoice.payment_intent.payment_method}
            )
    
    customer_pm = stripe.PaymentMethod.retrieve(
        customer_has_pm.invoice_settings.default_payment_method
    )
    print(customer_pm)
    
    customer_pm_details = {
        "brand": customer_pm.card.brand, 
        "last4": customer_pm.card.last4, 
        "last4": customer_pm.card.exp_month, 
        "last4": customer_pm.card.exp_year, 
    }
    


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
        
        
        

        # TODO: remove?
        # try:
        #     order_exists = Order.objects.get(
        #         stripe_invoice_id=subscription.latest_invoice.id)
        # except:
        #     order_exists = False
    
        request.session['package_selection'] = ""
        storage = messages.get_messages(request)
        storage.used = True
        messages.success(request, "You have successfully subscribed!")
        return redirect('get_my_orders')

    
    # Send end of current period to context
    if subscription and subscription.plan.id is not free_package_id:
        
        upcoming_inv = stripe.Invoice.upcoming(
            customer=user.stripe_customer_id,
        )
        next_period_start = datetime.fromtimestamp(upcoming_inv.next_payment_attempt).strftime(
            '%d %b %y') 
        current_end = datetime.fromtimestamp(subscription.current_period_end).strftime(
            '%d %b %y')
    else:
        next_period_start = ""
        current_end = datetime.fromtimestamp(subscription.current_period_end).strftime(
            '%d %b %y')

    # If user attempting to purchase the same subscription, send them to their orders
    if sub_price_id == package_stripe_id and latest_bill_paid == "paid":
        messages.error(request, "You are already subscribed to this package!")
        return redirect('get_my_orders')
    elif latest_bill_paid == 'paid':
        sub_is_change = True
        print("Sub is change?")
    else: 
        sub_is_change = False
        print("Sub is new")

    context = {
        "stripe_public_key": stripe_pk,
        'subId': subscription.id,
        'stripe_client_secret': subscription.latest_invoice.payment_intent.client_secret,
        'package_selected': package_item,
        'upgrade': sub_is_change,
        'next_period_start': next_period_start,
        'current_period_end': current_end,
        'customer_pm_details': customer_pm_details,
    }

    return render(request, 'checkout/confirm_order.html', context)


def cancel_abandoned_subscription(request):
    """ Call this function when user leaves page to destroy the subscription created """

    if request.method == "POST":
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
        return HttpResponse(content="Subscription has been removed", status=200)

    return HttpResponse(content="No further action required", status=200)


def checkout(request):

    return render(request, 'checkout/checkout.html')