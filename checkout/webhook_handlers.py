from django.http import HttpResponse
from django.shortcuts import render, redirect, reverse
from django.contrib import messages
from packages.models import Package
from users.models import MyAccount
from users.forms import UpdateUserPackage
from checkout.forms import OrderForm

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
        
        user_email = self.request.user
        user = MyAccount.objects.get(email=user_email)
        print("THE USER", user)
        name = user.first_name + " " + user.last_name
        package_selection = self.request.session['package_selection']['package_id']
        stripe_customer = self.request.session['package_selection']['stripe_cus']
        stripe_price_id = self.request.session['package_selection']['stripe_price_id']
        current_package = Package.objects.get(pk=package_selection)

        #  Update user profile with new package
        profile_form_data = {
            "package_tier": current_package.tier,
            "package_name": current_package,
            }
        profile_form = UpdateUserPackage(
            profile_form_data, instance=self.request.user)

        #  Create new order when payment successful
        order_form_data = {
                "buyer_name": name.title(),
                "buyer_email": self.request.user,
                "package_purchased": current_package,
                "order_total": current_package.price,
            }
        order_form = OrderForm(order_form_data)
        
        # Save forms if valid
        if order_form.is_valid() and profile_form.is_valid():
            order = order_form.save()
            profile_form.save()
            return redirect(reverse('order_confirmation', args=[order.order_id]))
        else:
            print("errors order:", order_form.errors)
            messages.error(self.request, "There was an error in your form")
        return HttpResponse(content=f'Webhook received: {event["type"]}', status=200)
    
    def handle_payment_failed_event(self, event):
        """ Handle webhook event when Stripe payment fails"""
        return HttpResponse(content=f'Webhook received: {event["type"]}', status=200) 