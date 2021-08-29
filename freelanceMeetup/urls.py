"""freelanceMeetup URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls import handler404, handler500
from django.contrib import admin
from django.conf import settings
from django.urls import path, include
from django.conf.urls.static import static
from .views import err_404, err_500


urlpatterns = [
    path('admin/', admin.site.urls),
    path('account/', include('allauth.urls')),
    path('profile/', include('users.urls')),
    path('packages/', include('packages.urls')),
    path('checkout/', include('checkout.urls')),
    path('freelancers/', include('users.urls')),
    path('', include('events.urls')),
    path('', include('home.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


if settings.DEBUG: 
    urlpatterns += [
        path('404/', err_404, name='404'),
        path('500/', err_500, name='500'),
        ]

handler404 = 'freelanceMeetup.views.err_404'
handler500 = 'freelanceMeetup.views.err_500'
