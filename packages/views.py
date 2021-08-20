from django.shortcuts import render
from .models import Package
from users.models import MyAccount

# Create your views here.

def package_index(request):
    context = {}
    packages = Package.objects.all()

    print(request.user)

    # Check if user authenticated & show current package if yes
    if request.user.is_authenticated:
        user = MyAccount.objects.get(email=request.user)
        users_package = Package.objects.get(tier=user.package_tier)

        if user.package_tier:
            context = {
                'users_package': users_package.tier,
                'packages': packages
            }
            return render(request, 'packages/packages.html', context)    
    else: 
        context['account_required'] = True    
    context['packages'] = packages

    return render(request, 'packages/packages.html', context)