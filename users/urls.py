from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('dashboard/', views.account_dashboard, name="account_dashboard"),
    path('dashboard/get_orders/', views.dashboard_my_orders, name="get_my_orders"),
    path('<username>/', views.view_profile, name="view_profile"),
    path('register/', views.CustomRegistrationView, name="registration"),
    path('send_email_verify', views.resend_verification_email, name="send_verify_email"),
]