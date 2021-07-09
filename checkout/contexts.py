

from django.conf import settings


def order_summary(request):

    package_selected = 0  # pk of the package item
    package_cost = 0

    context = {
        'package_selected': package_selected,
        'package_cost': package_cost
    }

    return context