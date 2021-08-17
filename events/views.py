from django.shortcuts import render

# Create your views here.

def event_listings(request):
    return render(request, 'events/all_events_list.html')
