from django.shortcuts import render, redirect

# Create your views here.

def package_selection(request, package_id):

    context = {}
    package_selection = request.session.get('package_selection', {})

    package_selection['package_id'] = package_id
    request.session['package_selection'] = package_selection
    
    context['p_selected'] = request.session
    print(context['p_selected'], "session: ", request.session['package_selection'])

    return redirect(order_summary)


def order_summary(request):
    return render(request, 'checkout/order_summary.html')


def checkout(request):
    return render(request, 'checkout/checkout.html')

