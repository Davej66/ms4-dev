from django.shortcuts import render

# Create your views here.

def event_listings(request):
    return render(request, 'events/event_listings.html')
