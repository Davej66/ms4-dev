from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('dashboard/', views.account_dashboard, name="account_dashboard"),
    path('dashboard/edit_profile', views.edit_profile, name="edit_profile"),
    path('dashboard/orders/', views.dashboard_my_orders, name="get_my_orders"),
    path('all/', views.all_users, name="all_users"),
    path('<username>/', views.view_profile, name="view_profile"),
    path('register/', views.CustomRegistrationView, name="registration"),
    path('ajax/add_friend/<other_user>', views.add_friend, name="add_friend"),
    path('ajax/cancel_friend/<other_user>', views.cancel_friend, name="cancel_friend"),
    path('ajax/accept_friend/<other_user>', views.accept_friend, name="accept_friend"),
    path('ajax/decline_friend/<other_user>', views.decline_friend, name="decline_friend"),
    path('ajax/remove_friend/<other_user>', views.remove_friend, name="remove_friend"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)