from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.checkout, name="checkout"),
    path('summary/', views.order_summary, name="summary"),
    path('package_select/<package_id>', views.package_selection, name="package_selection"),
    path('confirmation/<order_id>', views.order_confirmation, name="order_confirmation"),
    path('create_subscription', views.create_stripe_subscription, name="create_subcription"),
]