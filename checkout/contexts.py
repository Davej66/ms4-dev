

from django.conf import settings
from django.shortcuts import get_object_or_404
from packages.models import Package


def order_summary(request):

    package_selected = request.session['package_selection']
    package_cost = 0

    package = get_object_or_404(Package, pk=package_selected['package_id'])
    print(package_selected)

    context = {
        'package_selected': package_selected,
        'package_cost': package_cost,
        'package': package
    }

    return context