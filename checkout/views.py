from django.shortcuts import render, redirect, get_object_or_404, reverse
from django.http import JsonResponse
from django.conf import settings
from django.contrib import messages
from .contexts import order_summary_context
from .forms import OrderForm
from .models import Order
from users.forms import UpdateUserPackage
from users.models import MyAccount
from packages.models import Package

import stripe
import json
# Create your views here.


def package_selection(request, package_id):

    context = {}
    package_selection = request.session.get('package_selection', {})

    package_selection['package_id'] = package_id
    request.session['package_selection'] = package_selection

    context['p_selected'] = request.session
    print(context['p_selected'], "session: ",
          request.session['package_selection'])

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
        # Create a Stripe customer for subscription
        try:
            # Create a new customer object
            customer = stripe.Customer.create(
                email = user_email
            )

            stripe_customer = customer.id
            
            print("cus", stripe_customer, "type", type(stripe_customer))
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
                "package_name": current_package,
                "stripe_customer_id": stripe_customer
            }
            order_form = OrderForm(form_data)
            profile_form = UpdateUserPackage(
                profile_form_data, instance=request.user)
            print("errors order:", order_form.errors, "prf", profile_form.errors)
            if order_form.is_valid() and profile_form.is_valid():
                print("form can be saved")
                order = order_form.save()
                profile_form.save()
                return redirect(reverse('order_confirmation', args=[order.order_id]))
            else:
                messages.error(request, "There was an error in your form")
        
        except Exception as e:
            error = str(e)
            print("error", e)    
            return error

    else:
        total_cost = current_package.price
        stripe_total = round(total_cost * 100)
        stripe.api_key = stripe_sk
        intent = stripe.PaymentIntent.create(
            amount=stripe_total,
            currency=settings.STRIPE_CURRENCY
        )
        context = {
            "stripe_public_key": stripe_pk,
            "stripe_client_secret": intent.client_secret
        }

        return render(request, 'checkout/order_summary.html', context)

    return render(request, 'checkout/checkout.html')


def checkout(request):

    return render(request, 'checkout/checkout.html')


def order_confirmation(request, order_id):

    user = MyAccount.objects.get(email=request.user)
    stripe_customer_id = user.stripe_customer_id
    order = get_object_or_404(Order, order_id=order_id)
    print('cus id', stripe_customer_id)    
    messages.success(request, "Order confirmed")
    context = {
        'order': order,
        'package': order.package_purchased,
        'customer': stripe_customer_id

    }

    return render(request, 'checkout/order_confirmation.html', context)
