from django.http import HttpResponse

class StripeWH_Handler:
    """Class to handle Stripe Webhooks"""

    def __init__(self, request):
        self.request = request

    
    def handle_stripe_event(self, event):
        """ Handle webhook event and return response with information"""
        return HttpResponse(content=f'Webhook received: {event["type"]}', status=200)
        
    def handle_subscription_create_event(self, event):
        """ Handle webhook event when Stripe subscription is created"""
        return HttpResponse(content=f'Webhook received: {event["type"]}', status=200)
    
    def handle_subscription_update_event(self, event):
        """ Handle webhook event when Stripe subscription is updated"""
        return HttpResponse(content=f'Webhook received: {event["type"]}', status=200)
        
    def handle_payment_succeeded_event(self, event):
        """ Handle webhook event when Stripe payment succeeds"""
        return HttpResponse(content=f'Webhook received: {event["type"]}', status=200)
    
    def handle_payment_failed_event(self, event):
        """ Handle webhook event when Stripe payment fails"""
        return HttpResponse(content=f'Webhook received: {event["type"]}', status=200) 