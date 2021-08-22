from django.http import HttpResponse
from django.shortcuts import render, redirect, reverse
from django.contrib import messages
from django.conf import settings
from packages.models import Package
from users.models import MyAccount
from checkout.models import Order
from users.forms import UpdateUserPackage
from checkout.forms import OrderForm

import time 
import stripe
class StripeWH_Handler:
    """Class to handle Stripe Webhooks"""

    def __init__(self, request):
        self.request = request

    
    def handle_stripe_event(self, event):
        """ Handle webhook event and return response with information"""
        return HttpResponse(content=f'Unhandled webhook received: {event["type"]}', status=200)
        

    def handle_subscription_create_event(self, event):
        """ Handle webhook event when Stripe subscription is created"""
        return HttpResponse(content=f'Webhook received: {event["type"]}', status=200)
    

    def handle_subscription_update_event(self, event):
        """ Handle webhook event when Stripe subscription is updated"""
        
        subscription = event.data.object
        price_id = subscription['items']['data'][0].plan.id
        stripe_customer = subscription.customer
        user = MyAccount.objects.get(stripe_customer_id=stripe_customer)
        package = Package.objects.get(stripe_price_id=price_id)
        print("Sub change ",user.package_tier, package.tier)

        if user.package_tier != package.tier:
            try:
                user.package_tier = package.tier
                user.package_name = package.name
                user.save()
            except Exception as e:
                return HttpResponse(content=f'Webhook received: {event["type"]}, \
                                    but could not update user: {e}', status=500)
        return HttpResponse(content=f'Webhook received: {event["type"]}', status=200)
    

    def handle_subscription_deleted_event(self, event):
        """ Handle webhook event when Stripe subscription is deleted"""
        
        subscription = event.data.object
        stripe_customer = subscription.customer
        user = MyAccount.objects.get(stripe_customer_id=stripe_customer)
        
        user.stripe_subscription_id = ""
        user.save()
        
        return HttpResponse(content=f'Webhook received: {event["type"]}', status=200)
    
    
    def handle_customer_deleted_event(self, event):
        """ Handle webhook event when Stripe customer is deleted - 
            delete corresponding fields in user account"""
        
        customer = event.data.object
        user = MyAccount.objects.get(stripe_customer_id=customer.id)
        
        user.stripe_customer_id = ""
        user.stripe_subscription_id = ""
        user.events_remaining_in_package = 1
        user.package_tier = 1
        user.package_name = "Free Account"
        user.save()
        
        return HttpResponse(content=f'Webhook received: {event["type"]}', status=200)


    def handle_payment_succeeded_event(self, event):
        """ Handle webhook event when Stripe payment succeeds"""

        stripe_pk = settings.STRIPE_PUBLIC_KEY
        stripe_sk = settings.STRIPE_SECRET_KEY
        stripe.api_key = stripe_sk
    
        intent = event.data.object
        invoice_id = intent.invoice
        stripe_customer = intent.customer
        user = MyAccount.objects.get(stripe_customer_id=stripe_customer)
        name = user.first_name + " " + user.last_name
        package_cost = intent.amount / 100
        package = Package.objects.get(price=package_cost)
        
        try:
            # Create new order after payment
            order_form_data = {
                "buyer_name": name,
                "customer": user,
                "package_purchased": package,
                "order_total": package.price,
                "stripe_invoice_id": invoice_id
                }
            order_form = OrderForm(order_form_data)
            
            if order_form.is_valid():
                order_form.save()
            
            
            get_events_attending = Event.objects.filter(registrants=user).count()
            user.events_remaining_in_package = package.event_limit - get_events_attending
            user.save()
            
            # Get the order number and add to the Stripe invoice
            order = Order.objects.get(stripe_invoice_id=invoice_id)
                
            current_inv = stripe.Invoice.modify(
                invoice_id,
                metadata={"order_id": order.order_id}
                )

            return HttpResponse(content=f'Webhook received: {event["type"]} | \
            Order created successfully', status=200)
        except:
            pass
        return HttpResponse(content=f'Webhook received: {event["type"]}', status=200)
    

    def handle_payment_failed_event(self, event):
        """ Handle webhook event when Stripe payment fails"""
        return HttpResponse(content=f'Webhook received: {event["type"]}', status=200) 