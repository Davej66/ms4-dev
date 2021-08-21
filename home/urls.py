from django.contrib import admin
from django.urls import path

from .views import index, privacy, contact


urlpatterns = [
    path('', index, name="home"),
    path('privacy/', privacy, name="privacy"),
    path('contact/', contact, name="contact"),
]