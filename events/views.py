from django.shortcuts import render
from django.shortcuts import render, HttpResponse, get_object_or_404
from django.http import JsonResponse
from django.conf import settings
from django.contrib import messages
from django.db.models import Q
from django.template.loader import render_to_string
from allauth.account.decorators import verified_email_required
from .models import Event
from users.models import MyAccount

# Create your views here.

def event_listings(request):
    
    all_events = Event.objects.get(title="Test Event")
    print("THIS IS THE PRINT",all_events.description, all_events.registrants.all())
    
    # registrant_one = all_events.registrants.get(email='bradleyh.cooney@gmail.com')
    registrant_two = MyAccount.objects.get(email='martacraig@premiant.com')
    print("THIS IS USER", registrant_two)
    
    # all_events.registrants.remove(registrant_one)
    all_events.registrants.add(registrant_two)
    
    print("THIS FINAL",all_events.registrants.all())
    
    context = {
        'events': all_events
    }
    
    return render(request, 'events/all_events_list.html', context)


""" Event Registration / Cancellation Functions """

@verified_email_required
def event_register(request, **kwargs):
    """ Register for an event """
    if request.is_ajax and request.method == "GET":
        event_id = kwargs.get('event_id')
        event_instance = Event.objects.get(pk=event_id)
        
        # Decline the request
        try:
            event_instance.registrants.add(request.user)
        except:
            messages.error(request, 
                           "We ran into an issue processing this request, please try again")
        
        return JsonResponse({"response":"User successfully registered for this event", 
                             "buttonId": event_id,
                            "type": "register"})


@verified_email_required
def cancel_reg(request, **kwargs):
    """ Cancel previous existing registration """
    if request.is_ajax and request.method == "GET":
        event_id = kwargs.get('event_id')
        event_instance = Event.objects.get(pk=event_id)
        
        # Decline the request
        try:
            event_instance.registrants.remove(request.user)
        except:
            messages.error(request, 
                           "We could no longer find you in the registration" +
                           "list for this event, so no further action is needed.")
        
        return JsonResponse({"response":"User successfully cancelled their registration for this event", 
                             "buttonId": event_id,
                            "type": "cancel_reg"})
