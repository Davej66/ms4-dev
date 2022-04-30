from django.http import HttpResponse
from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.contrib import messages
from django.conf import settings
from packages.models import Package
from users.models import MyAccount
from checkout.models import Order
from events.models import Event
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

        stripe_pk = settings.STRIPE_PUBLIC_KEY_MS4
        stripe_sk = settings.STRIPE_SECRET_KEY_MS4
        stripe.api_key = stripe_sk
    
        intent = event.data.object
        try: 
            invoice_id = intent.invoice
        except:
            invoice_id = "null"
        stripe_customer = intent.customer
        user = get_object_or_404(MyAccount, stripe_customer_id=stripe_customer)
        
        subscription = stripe.Subscription.retrieve(
            user.stripe_subscription_id
        )
        
        price_id = subscription['items']['data'][0].plan.id
        package = Package.objects.get(stripe_price_id=price_id)
        
        if not user: 
            return HttpResponse(content=f'Webhook received: {event["type"]} | \
            No user found', status=200)
            
        name = user.first_name + " " + user.last_name
        
        get_events_attending = Event.objects.filter(registrants=user).count()
        user_events_remaining = package.event_limit - get_events_attending

        if user_events_remaining < 0:
            user_events_allowance = 0
        else:
            user_events_allowance = user_events_remaining
        
        user.events_remaining_in_package = user_events_allowance
        user.package_tier = package.tier
        user.package_name = package.name
        user.is_blocked = False
        user.save()
            
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
            order_form.save()
            
            
            
            # Get the order number and add to the Stripe invoice
            order = Order.objects.get(stripe_invoice_id=invoice_id)
            
            try:
                stripe.Invoice.modify(
                    invoice_id,
                    metadata={"order_id": order.order_id}
                    )
            except:
                pass

            return HttpResponse(content=f'Webhook received: {event["type"]} | \
            Order created successfully', status=200)
        except:
            pass
        return HttpResponse(content=f'Webhook received: {event["type"]}', status=200)
    
    
    def handle_invoice_payment_succeeded_event(self, event):
        """ Handle webhook event when Stripe charge succeeds. Reset package tier and event allowance."""
        
        stripe_pk = settings.STRIPE_PUBLIC_KEY
        stripe_sk = settings.STRIPE_SECRET_KEY
        stripe.api_key = stripe_sk
    
        charge = event.data.object
        stripe_customer = charge.customer
        user = get_object_or_404(MyAccount, stripe_customer_id=stripe_customer)
        
        subscription = stripe.Subscription.retrieve(
            user.stripe_subscription_id
        )
        
        price_id = subscription['items']['data'][0].plan.id
        package = Package.objects.get(stripe_price_id=price_id)
        
        if not user: 
            return HttpResponse(content=f'Webhook received: {event["type"]} | \
            No user found', status=200)
            
        get_events_attending = Event.objects.filter(registrants=user).count()
        user_events_remaining = package.event_limit - get_events_attending

        if user_events_remaining < 0:
            user_events_allowance = 0
        else:
            user_events_allowance = user_events_remaining
        
        user.events_remaining_in_package = user_events_allowance
        user.is_blocked = False
        user.package_tier = package.tier
        user.package_name = package.name
        user.save()
        
        return HttpResponse(content=f'Webhook received: {event["type"]}', status=200) 
    
    
    def handle_invoice_paid_event(self, event):
        """ Handle webhook event when Stripe invoice paid"""
        
        intent = event.data.object
        stripe_customer = intent.customer
        user = MyAccount.objects.get(stripe_customer_id=stripe_customer)
         
        user.is_blocked = False
        user.save()
        
        return HttpResponse(content=f'Webhook received: {event["type"]}', status=200) 
    
    
    def handle_payment_cancelled_event(self, event):
        """ Handle webhook event when Stripe payment intent cancels due to failed invoice"""
        intent = event.data.object
        cancel_reason = intent.cancellation_reason
        stripe_customer = intent.customer
        user = MyAccount.objects.get(stripe_customer_id=stripe_customer)
        
        if cancel_reason == "failed_invoice":
            user.is_blocked = True
            user.save()
        
        return HttpResponse(content=f'Webhook received: {event["type"]}', status=200) 
    

    def handle_payment_failed_event(self, event):
        """ Handle webhook event when Stripe payment fails. Block the user account until payment made successfully"""
        
        intent = event.data.object
        stripe_customer = intent.customer
        user = MyAccount.objects.get(stripe_customer_id=stripe_customer)
        
        user.is_blocked = True
        user.save()
        
        return HttpResponse(content=f'Webhook received: {event["type"]}', status=200) 
