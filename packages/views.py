from django.shortcuts import render
from django.conf import settings
from .models import Package
from users.models import MyAccount

import stripe


def package_index(request):
    context = {}
    packages = Package.objects.all()
    
    stripe_pk = settings.STRIPE_PUBLIC_KEY
    stripe_sk = settings.STRIPE_SECRET_KEY
    stripe.api_key = stripe_sk
    

    # Check if user authenticated & show current package if yes
    if request.user.is_authenticated:
        user = MyAccount.objects.get(email=request.user)
        users_package = Package.objects.get(tier=user.package_tier)
        
        try:
            """Check if subscription is pending change"""
            
            subscription = stripe.Subscription.retrieve(
                user.stripe_subscription_id
            )
            
            sub_package = Package.objects.get(stripe_price_id=subscription.plan.id)
            
            if sub_package.tier > users_package.tier:
                sub_change = "upgrade" 
            elif sub_package.tier < users_package.tier:
                sub_change = "downgrade" 
            else: 
                sub_change = "none" 
            
        except:
            sub_change = "none"

        if user.package_tier:
            context = {
                'users_package': users_package.tier,
                'packages': packages,
                'sub_change': sub_change
            }
            return render(request, 'packages/packages.html', context)    
    else: 
        context['account_required'] = True    
    context['packages'] = packages

    return render(request, 'packages/packages.html', context)