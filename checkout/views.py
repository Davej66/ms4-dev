from django.shortcuts import render, redirect, get_object_or_404, reverse, HttpResponse
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.conf import settings
from django.contrib import messages
from .contexts import order_summary_context
from .forms import OrderForm
from .models import Order
from users.forms import UpdateUserPackage, AddUserSubscription
from users.models import MyAccount
from packages.models import Package

import stripe
import json
# Create your views here.

@require_POST
def checkout_cach(request):
    # TODO Extend this out
    pid = request.POST.get('client_secret').split('_secret')[0]
    stripe.api_key = settings.STRIPE_SECRET_KEY
    stripe.Subscription.modify(pid, metadata={
        'email': request.user
    })


def package_selection(request, package_id):

    stripe_pk = settings.STRIPE_PUBLIC_KEY
    stripe_sk = settings.STRIPE_SECRET_KEY
    stripe.api_key = stripe_sk

    context = {}
    user_email = request.user
    package_selection = request.session.get('package_selection', {})


    package_selection['package_id'] = package_id
    package_object = Package.objects.get(pk=package_id)
    request.session['package_selection'] = package_selection
    context['p_selected'] = request.session

    current_user = MyAccount.objects.get(email=user_email)
    user_stripe_cus_id = current_user.stripe_customer_id
    print("I am a stripe user",user_stripe_cus_id)

    if user_stripe_cus_id is None:
        try:
            # Create a new customer object
            customer = stripe.Customer.create(
                email = user_email
                )
            package_selection['stripe_cus'] = customer.id
            package_selection['stripe_price_id'] = package_object.stripe_price_id
            return redirect(order_summary)
            
        except Exception as e:
            error = str(e)
            print("error", e)    
            return error
    else:
        try:
            package_selection['stripe_cus'] = user_stripe_cus_id
            package_selection['stripe_price_id'] = package_object.stripe_price_id
            return redirect(order_summary)
            
        except Exception as e:
            error = str(e)
            print("error", e)    
            return error

    print(context['p_selected'], "session: ",
          request.session['package_selection'])

    return redirect(order_summary)


def order_summary(request):

    stripe_pk = settings.STRIPE_PUBLIC_KEY
    stripe_sk = settings.STRIPE_SECRET_KEY
    user_email = request.user
    user = MyAccount.objects.get(email=user_email)
    name = user.first_name + " " + user.last_name
    print("THIS USER IN VIEW",user)

    package_selection = request.session['package_selection']['package_id']
    stripe_customer = request.session['package_selection']['stripe_cus']
    stripe_price_id = request.session['package_selection']['stripe_price_id']
    current_package = Package.objects.get(pk=package_selection)
    
    print("who are ya", name)

    if not stripe_pk:
        messages.warning(request, "No public key found for Stripe")

    if request.method == 'POST':
        profile_form_data = {
            "package_tier": current_package.tier,
            "package_name": current_package,
            'stripe_customer_id': stripe_customer
            }
        order_form_data = {
                "buyer_name": name.title(),
                "buyer_email": user_email,
                "package_purchased": current_package,
                "order_total": current_package.price
            }
        profile_form = UpdateUserPackage(
            profile_form_data, instance=request.user)
        order_form = OrderForm(order_form_data)
        if order_form.is_valid() and profile_form.is_valid():
            order = order_form.save()
            profile_form.save()
            return redirect(reverse('order_confirmation', args=[order.order_id]))
        else:
            print("errors order in the view:",profile_form.errors, order_form.errors)
            messages.error(request, "There was an error in your form")
   
    context = {
        "stripe_public_key": stripe_pk,
        "stripe_price_id": stripe_price_id,
        "stripe_customer": stripe_customer,
        }

    return render(request, 'checkout/order_summary.html', context)


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


def create_stripe_subscription(request):

    stripe_pk = settings.STRIPE_PUBLIC_KEY
    stripe_sk = settings.STRIPE_SECRET_KEY
    stripe.api_key = stripe_sk

    data = json.loads(request.body)
    data_dict = dict(data)
    customer = data_dict['customerId']
    price_id = data_dict['priceId']
    print("the things",data_dict)
    # return JsonResponse(data)
    
    try:
        subscription = stripe.Subscription.create(
            customer= customer,
            items=[{
                'price': price_id
            }],
            payment_behavior='default_incomplete',
            expand=['latest_invoice.payment_intent'],
        )

        add_sub_form_data = {
            "stripe_subscription_id": subscription.id
            }

        profile_form = AddUserSubscription(
                add_sub_form_data, instance=request.user)
        print("prf", profile_form.errors)
        if profile_form.is_valid():
            profile_form.save()
        else:
            messages.error(request, "There has been an error updating your prescription. Please reload the page to try again.")
        
        return JsonResponse({'subId': subscription.id, 'clientSecret':subscription.latest_invoice.payment_intent.client_secret})
        
    except Exception as e:
        print("didnt work", e.user_message)
        return JsonResponse({'message': e.user_message}), 400