from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from events import views


urlpatterns = [
    path('meetups/', views.event_listings, name="event_listings"),
    path('meetups/ajax/event_register/<event_id>', views.event_register, name="event_register"),
    path('meetups/ajax/event_cancel/<event_id>', views.event_cancel, name="event_cancel"),
    path('meetups/create_event', views.create_event, name="create_event"),
    path('meetups/edit_event', views.edit_event, name="edit_event"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)