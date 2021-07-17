from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt 
from checkout.webhook_handlers import StripeWH_Handler

import stripe
import json

@require_POST
@csrf_exempt
def webhook(request):
    """ Listen for Stripe webhooks"""

    # Setup webhook
    wh_secret = settings.STRIPE_WH_SECRET
    stripe.api_key = settings.STRIPE_SECRET_KEY

    # Get webhook data
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    try:
        event = stripe.Event.construct_from(
        json.loads(payload.decode('utf-8')), sig_header, stripe.api_key
        )
    except ValueError as e:
        # Invalid payload
        print("not so Success")
        return HttpResponse(status=400)
    except Exception as e:
        print("Failed")
        return HttpResponse(content=e, status=400)

    
    print("Success")
    return HttpResponse(status=200)