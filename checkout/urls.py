from django.contrib import admin
from django.urls import path, include
from . import views
from .webhooks import webhook

urlpatterns = [
    path('confirm_order/', views.confirm_order, name="summary"),
    path('package_select/ajax/store_selection/', views.store_selection, name="store_package_selection"),
    path('destroy_sub/', views.cancel_abandoned_subscription, name="destroy_sub"),
    path('update_pm/', views.update_payment_method, name="update_pm"),
    path('wh/', webhook, name="webhook")
]