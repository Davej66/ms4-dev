from django.contrib import admin
from django.urls import path, include
from packages import views

urlpatterns = [
    path('', views.package_index, name="packages"),
]