from django.shortcuts import render
from django.shortcuts import render, HttpResponse, get_object_or_404
from django.http import JsonResponse
from django.conf import settings
from django.contrib import messages
from django.db.models import Q
from django.template.loader import render_to_string
from allauth.account.decorators import verified_email_required
from .models import Event
from friendship.models import Friend, FriendshipRequest
from users.models import MyAccount

import json


def event_listings(request):
    
    all_events = Event.objects.all()
    
    query = Q(to_user=request.user) | Q(from_user=request.user)
    connection_requests = FriendshipRequest.objects.filter(query)
    user_connections = Friend.objects.friends(request.user)
    user_connections_list = []
    
    for uid in user_connections:
        user_connections_list.append(uid.pk)
    
    if request.is_ajax and request.method == "POST":
        query = request.POST['event_search'] 
        industry_query = request.POST['industry']
        
        if query != "":
            queries = Q(title__icontains=query) | Q(description__icontains=query) | Q(
                location__icontains=query) | Q(industry__icontains=query)
        else: 
            queries = Q(industry=industry_query)
        
        results = Event.objects.filter(queries)
        
        context = {
            'search_results': results
        }
        payload = render_to_string('events/includes/ajax_event_search_results.html', context)
        return HttpResponse(json.dumps(payload), content_type="application/json")
    
    context = {
        'events': all_events,
        'pending_friend_reqs': connection_requests,
        'current_connections': user_connections
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
def event_cancel(request, **kwargs):
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
