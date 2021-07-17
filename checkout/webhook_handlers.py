from django.http import HttpResponse

class StripeWH_Handler:
    """Class to handle Stripe Webhooks"""

    def __init__(self, request):
        self.request = request

    
    def handle_stripe_event(self, event):
        """ Handle webhook event and return response with information"""
        return HttpResponse(content=f'Webhook received: {event['type']}', status=200)