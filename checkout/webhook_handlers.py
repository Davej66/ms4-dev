from django.http import HttpResponse
from django.shortcuts import render, redirect, reverse
from django.contrib import messages
from packages.models import Package
from users.models import MyAccount
from checkout.models import Order
from users.forms import UpdateUserPackage
from checkout.forms import OrderForm

import time 
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
        return HttpResponse(content=f'Webhook received: {event["type"]}', status=200)
        
    def handle_payment_succeeded_event(self, event):
        """ Handle webhook event when Stripe payment succeeds"""
        

        intent = event.data.object
        invoice_id = intent.invoice
        stripe_customer = intent.customer
        user = MyAccount.objects.get(stripe_customer_id=stripe_customer)
        name = user.first_name + " " + user.last_name
        package_cost = intent.amount / 100
        package = Package.objects.get(price=package_cost)
        print("this is the intent", package)
        
        order_exists = False
        attempt = 1

        while attempt <= 5:
            try:
                order = Order.objects.get(stripe_invoice_id=invoice_id)
                order_exists = True
                break
            except Order.DoesNotExist:
                attempt += 1
                time.sleep(1)

        if order_exists:
            return HttpResponse(content=f'Webhook received: {event["type"]} | \
                SUCCESS: Order in database', status=200)
        
        else:
            order = None
            try:
                order_form_data = {
                "buyer_name": name,
                "buyer_email": user.email,
                "package_purchased": package.name,
                "order_total": package.price,
                "stripe_invoice_id": invoice_id
                }
                order_form = OrderForm(order_form_data)
                if order_form.is_valid():
                    order = order_form.save()
                return HttpResponse(content=f'Webhook received: {event["type"]} | \
                ORDER CREATED: No order found in database', status=200)
            except Exception as e:
                pass
        return HttpResponse(content=f'Webhook received: {event["type"]}', status=200)
    
    def handle_payment_failed_event(self, event):
        """ Handle webhook event when Stripe payment fails"""
        return HttpResponse(content=f'Webhook received: {event["type"]}', status=200) 