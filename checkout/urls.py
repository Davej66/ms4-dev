from django.contrib import admin
from django.urls import path, include
from . import views
from .webhooks import webhook

urlpatterns = [
    path('', views.checkout, name="checkout"),
    path('confirm_order/', views.confirm_order, name="summary"),
    path('package_select/ajax/store_selection/', views.store_selection, name="store_package_selection"),
    # path('confirm_order/', views.confirm_order, name="confirm_order"),
    path('create_subscription', views.create_stripe_subscription, name="create_subcription"),
    path('update_subscription', views.update_stripe_subscription, name="update_subscription"),
    path('invoices', views.list_stripe_invoices, name="my_invoices"),
    path('wh/', webhook, name="webhook")
]