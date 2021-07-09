from django.shortcuts import render

# Create your views here.

def package_index(request):
    return render(request, 'packages/packages.html')