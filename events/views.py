from django.shortcuts import (render, HttpResponse, get_object_or_404, redirect)
from django.http import JsonResponse
from django.conf import settings
from django.contrib import messages
from django.db.models import Q
from django.template.loader import render_to_string
from allauth.account.decorators import verified_email_required
from .models import Event
from .forms import CreateEventForm
from friendship.models import Friend, FriendshipRequest
from users.models import MyAccount

import json

@verified_email_required
def event_listings(request):
    
    all_events = Event.objects.all().order_by('start_datetime')
    
    user = request.user
    query = Q(to_user=request.user) | Q(from_user=request.user)
    connection_requests = FriendshipRequest.objects.filter(query)
    user_connections = Friend.objects.friends(request.user)
    user_connections_list = []
    
    # Get the user event registration cap based on package
    if user.package_tier == 1:
        user_event_limit = 1
    elif user.package_tier == 2:
        user_event_limit = 5
    else:
        user_event_limit = 10
    
    # Get the friends and add their ID to a list
    for uid in user_connections:
        user_connections_list.append(uid.pk)
    
    if request.is_ajax and request.method == "POST":
        query = request.POST['event_search'] 
        industry_query = request.POST['industry']
        
        if query != "":
            queries = Q(title__icontains=query) | Q(description__icontains=query) | Q(
                location__icontains=query) | Q(industry__icontains=query)
        elif industry_query == "All":
            queries = ~Q(industry=industry_query)
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
        'current_connections': user_connections,
        'event_limit': user_event_limit
    }
    
    return render(request, 'events/all_events_list.html', context)


@verified_email_required
def create_event(request):

    if request.method == 'POST':

        get_startdate = request.POST.get('start_datetime')
        comma_rem_start = get_startdate.replace(',', '')
        print("start date",comma_rem_start)
        
        form = CreateEventForm(request.POST, request.FILES)
        
        if form.is_valid():
            form.save()
            messages.success(request, "Your event has been created!")
            return redirect('event_listings')
        else:
            messages.error(
                request, "Form could not be submitted, please try again!")

    return render(request, 'events/all_events_list.html')


""" Event Registration / Cancellation Functions """

@verified_email_required
def event_register(request, **kwargs):
    """ Register for an event """
    if request.is_ajax and request.method == "GET":
        event_id = kwargs.get('event_id')
        event_instance = Event.objects.get(pk=event_id)
        user = request.user
        
        user_events_remaining = MyAccount.objects.get(pk=request.user.pk).events_remaining_in_package
        if user_events_remaining != 0:    
            try:
                event_instance.registrants.add(request.user)
                user.events_remaining_in_package -= 1
                user.save()
            except:
                messages.error(request, 
                            "We ran into an issue processing this request, please try again")
            return JsonResponse({"response":"User successfully registered for this event", 
                             "buttonId": event_id, "type": "register"})
        else:
            return JsonResponse({"response":"Event limit for this account type reached", 
                                "buttonId": event_id, "type": "limit_reached"})
            
    return JsonResponse({"response":"An error occured, please try again", "type": "error"})


@verified_email_required
def event_cancel(request, **kwargs):
    """ Cancel previous existing registration """
    if request.is_ajax and request.method == "GET":
        event_id = kwargs.get('event_id')
        event_instance = Event.objects.get(pk=event_id)
        user = request.user
        
        user_events_remaining = MyAccount.objects.get(pk=request.user.pk).events_remaining_in_package
        
        # Set the limit for the user events based on packaged
        if user.package_tier == 1:
            user_event_limit = 1
        elif user.package_tier == 2:
            user_event_limit = 5
        else:
            user_event_limit = 10     
            
        try:
            event_instance.registrants.remove(request.user)
            if user_events_remaining < user_event_limit:
                user.events_remaining_in_package += 1
                user.save()
        except:
            messages.error(request, 
                           "We could no longer find you in the registration" +
                           "list for this event, so no further action is needed.")
        
        return JsonResponse({"response":"User successfully cancelled their registration for this event", 
                             "buttonId": event_id,
                            "type": "cancel_reg"})
