from django import http
from django.shortcuts import (
    render, redirect, get_object_or_404)
from django.http import JsonResponse, HttpResponse
from django.template.loader import render_to_string
from django.views.decorators.http import require_POST
from django.conf import settings
from django.contrib import messages
from allauth.account.decorators import verified_email_required
from .contexts import order_summary_context
from .forms import OrderForm
from .models import Order
from users.forms import UpdateUserPackage, AddUserSubscription
from users.models import MyAccount
from packages.models import Package
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

    if request.is_ajax():

        # Get the package id from the ajax request
        package = request.POST['package_id']
        request.session['package_selection'] = package
        return redirect('summary')

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

    # Determine if the subscription is an upgrade or new account 
    sub_is_upgrade = False

    package_selection = int(request.session['package_selection'])
    package_item = Package.objects.get(tier=package_selection)
    package_stripe_id = package_item.stripe_price_id

    if user.stripe_subscription_id:
        sub_price_id = stripe.Subscription.retrieve(
            user.stripe_subscription_id
        ).plan.id
    print(sub_price_id, package_stripe_id)

    if not stripe_pk:
        messages.warning(request, "No public key found for Stripe")

    # If user attempting to purchase the same subscription, send them to their orders
    if sub_price_id is package_stripe_id:
        messages.error(request, "You are already subscribed to this package!")
        return redirect('get_my_orders')
    elif sub_price_id:
        sub_is_upgrade = True
    else:
        sub_is_upgrade = False

    print('sub_is_upgrade', sub_is_upgrade)

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

    if request.method == 'POST':

        user.package_tier = package_item.tier
        user.package_name = package_item.name
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.email = request.POST.get('email')
        user.save()

        # If user updates their details on form, update their account
        user_email = request.POST.get('email')
        name = request.POST.get('first_name') + " " + \
            request.POST.get('last_name')

        # Update the stripe customer with name and email
        stripe.Customer.modify(
            user.stripe_customer_id,
            email=user_email,
            name=name,
        )

        # Check if updated sub based on new package required and update if yes
        if sub_is_upgrade:
            subscription = stripe.Subscription.retrieve(user.stripe_subscription_id)
            stripe.Subscription.modify(
                subscription.id,
                cancel_at_period_end=False,
                proration_behavior='create_prorations',
                items=[{
                    'id': subscription['items']['data'][0].id,
                    'price': package_item.stripe_price_id,
                }]
            )

        try:
            order_exists = Order.objects.get(
                stripe_invoice_id=subscription.latest_invoice.id)
        except:
            order_exists = False
        print(subscription.latest_invoice)
        if not order_exists:
            order_form_data = {
                "buyer_name": name.title(),
                "buyer_email": user_email,
                "package_purchased": package_item,
                "order_total": package_item.price,
                "stripe_invoice_id": subscription.latest_invoice
            }
            order_form = OrderForm(order_form_data)
            if order_form.is_valid():
                order_form.save()

            else:
                messages.error(request, "There was an error in your form")

            messages.success(request, "Thank you for signing up," +
                             "you can see all previous orders in the 'My Orders' section below!")
            return redirect('get_my_orders')
        else:
            messages.success(request, "Looks like you already have a bill for this order." +
                             "You can see all previous orders in the 'My Orders' section below!")
            return redirect('get_my_orders')

    context = {
        "stripe_public_key": stripe_pk,
        'subId': subscription.id,
        'stripe_client_secret': subscription.latest_invoice.payment_intent.client_secret,
        'package_selected': package_item,
        'upgrade': sub_is_upgrade,
    }

    return render(request, 'checkout/confirm_order.html', context)


def checkout(request):

    return render(request, 'checkout/checkout.html')

# TODO - could delete below function
# Create a stripe subscription when package selected
# def create_stripe_subscription(request):
    # stripe_sk = settings.STRIPE_SECRET_KEY
    # stripe.api_key = stripe_sk

    # user = MyAccount.objects.get(email=request.user)
    # data = request.body
    # customer = data['customerId']
    # price_id = data['priceId']

    # if not user.stripe_subscription_id:
    #     try:
    #         subscription = stripe.Subscription.create(
    #             customer=customer,
    #             items=[{
    #                 'price': price_id
    #             }],
    #             payment_behavior='default_incomplete',
    #             expand=['latest_invoice.payment_intent'],
    #         )

    #         add_sub_form_data = {
    #             "stripe_subscription_id": subscription.id
    #         }

    #         profile_form = AddUserSubscription(
    #             add_sub_form_data, instance=request.user)
    #         print("prf", profile_form.errors)
    #         if profile_form.is_valid():
    #             profile_form.save()
    #         else:
    #             messages.error(
    #                 request, "There has been an error updating your subscription. Please reload the page to try again.")

    #         return JsonResponse({'subId': subscription.id, 'clientSecret': subscription.latest_invoice.payment_intent.client_secret})

    #     except Exception as e:
    #         print("didnt work", e.user_message)
    #         return JsonResponse({'message': e.user_message}), 400
    # else:
    #     subscription = stripe.Subscription.retrieve(
    #         user.stripe_subscription_id,
    #         expand=['latest_invoice.payment_intent'])
    #     print("Sub already exists", subscription)
    #     return HttpResponse(content="Subscription already exists for this user.", status=200)


@verified_email_required
def update_stripe_subscription(request):

    user = request.user
    stripe_sk = settings.STRIPE_SECRET_KEY
    stripe.api_key = stripe_sk

    user = MyAccount.objects.get(email=request.user)
    user_stripe_sub = user.stripe_subscription_id

    # if request.method is "POST":

    # new_price_id = Package.objects.get(tier=new_package).stripe_price_id

    # subscription = stripe.Subscription.modify(
    #     user_stripe_sub,
    #     )

    # get_subscription_item = subscription.items.data[0].id
    # print(get_subscription_item)
    # stripe.SubscriptionItem.modify(
    #     get_subscription_item,
    #     price={"id": new_price_id}
    #     )

    return render(request, 'checkout/update_subscription.html')


def order_confirmation(request, order_id):
    # stripe_pk = settings.STRIPE_PUBLIC_KEY
    stripe_sk = settings.STRIPE_SECRET_KEY
    stripe.api_key = stripe_sk

    user = MyAccount.objects.get(email=request.user)
    stripe_customer_id = user.stripe_customer_id
    order = get_object_or_404(Order, order_id=order_id)
    print('cus id', stripe_customer_id)
    messages.success(request, "Order confirmed")

    invoices = stripe.Invoice.list(
        limit=10,
        customer=stripe_customer_id)
    print("invoices", invoices)

    context = {
        'order': order,
        'package': order.package_purchased,
        'customer': stripe_customer_id
    }

    return render(request, 'checkout/order_confirmation.html', context)


# def list_stripe_invoices(request):

#     # stripe_pk = settings.STRIPE_PUBLIC_KEY
#     stripe_sk = settings.STRIPE_SECRET_KEY
#     stripe.api_key = stripe_sk

#     user = MyAccount.objects.get(email=request.user)
#     stripe_customer_id = user.stripe_customer_id

#     invoices = stripe.Invoice.list(
#         limit=10,
#         customer=stripe_customer_id)
#     print("invoices", invoices)
#     invoice_list = []

#     for i in invoices:
#         invoice_date = datetime.fromtimestamp(i.created).strftime(
#             '%Y-%m-%d %H:%M:%S')
#         start_date = datetime.fromtimestamp(i.period_start).strftime(
#             '%Y-%m-%d %H:%M:%S')
#         end_date = datetime.fromtimestamp(i.period_end).strftime(
#             '%Y-%m-%d %H:%M:%S')
#         invoice_data = {
#             "invoice_date": invoice_date,
#             "date_start": start_date,
#             "date_end": end_date,
#             "amount": i.lines.data[0].amount / 100,
#             "download_url": i.invoice_pdf
#         }
#         invoice_list.append(invoice_data)

#     print(invoice_list)
#     context = {
#         'invoices': invoice_list
#     }
#     return render(request, 'checkout/invoices.html', context)
