from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('dashboard/', views.account_dashboard, name="account_dashboard"),
    path('dashboard/edit_profile', views.edit_profile, name="edit_profile"),
    path('dashboard/get_orders/', views.dashboard_my_orders, name="get_my_orders"),
    path('<username>/', views.view_profile, name="view_profile"),
    path('register/', views.CustomRegistrationView, name="registration"),
]