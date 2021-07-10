

from django.conf import settings
from django.shortcuts import get_object_or_404
from packages.models import Package


def order_summary_context(request):

    context = {}
    

    if 'package_selected' in request.session:
        package_selected = request.session['package_selection']
        package = get_object_or_404(Package, pk=package_selected['package_id'])
        package_cost = Package.price

        context = {
            'package_selected': package_selected,
            'package_cost': package_cost,
            'package': package
        }

    print("session context", context)
    
    return context
