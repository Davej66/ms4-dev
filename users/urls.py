from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('dashboard/', views.account_dashboard, name="account_dashboard"),
    path('dashboard/get_orders', views.dashboard_my_orders, name="get_my_orders"),
]