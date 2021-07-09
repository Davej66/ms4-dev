from django.shortcuts import render
from .models import Package

# Create your views here.

def package_index(request):
    context = {}
    packages = Package.objects.all()

    context['packages'] = packages

    return render(request, 'packages/packages.html', context)