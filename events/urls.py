from django.contrib import admin
from django.urls import path, include
from events import views


urlpatterns = [
    path('', views.event_listings, name="event_listings"),
]