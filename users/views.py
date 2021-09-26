from django.db import connection
from django.db.models.query_utils import PathInfo
from django.shortcuts import (
    render, HttpResponse, get_object_or_404, redirect)
from django.http import JsonResponse, response
from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail, EmailMessage
from django.db.models import Q
from django.template.loader import render_to_string
from allauth.account.decorators import verified_email_required
from django.views.decorators.cache import never_cache
from allauth.account.views import SignupView
from allauth.account.utils import send_email_confirmation, user_pk_to_url_str
from users.forms import RegistrationForm, EditProfileForm
from packages.models import Package
from events.models import Event
from friendship.models import Friend, FriendshipRequest
from users.models import MyAccount
from datetime import datetime

import stripe
import json

# Create customised context for Allauth registration. Credits to Mikeec3
# In this StackOverflow thread: https://stackoverflow.com/questions/29499449/django-allauth-login-signup-form-on-homepage


class CustomRegistrationView(SignupView):

    # Get the original signup form and add the custom form to this
    def get_context_data(self, **kwargs):
        context = super(CustomRegistrationView,
                        self).get_context_data(**kwargs)
        context['reg_form'] = RegistrationForm()
        return context


register = CustomRegistrationView.as_view()


@verified_email_required
@never_cache
def account_dashboard(request):

    user = MyAccount.objects.get(email=request.user)
    full_name = user.first_name + " " + user.last_name
    user_package = user.package_name
    profile_complete = user.profile_completed
    pending_reqs_to_user = Friend.objects.unread_requests(
        user=request.user)
    user_events = request.user.attendees.all()
    user_friends_count = len(Friend.objects.friends(request.user))

    requested_users = []

    for int in pending_reqs_to_user:
        get_requestor = get_object_or_404(MyAccount, email=int.from_user)
        requested_users.append(get_requestor)

    context = {
        'full_name': full_name.title(),
        'package': user_package,
        'pending_friend_reqs': requested_users,
        'user_events': user_events,
        'user_friends': user_friends_count,
    }

    if not profile_complete:
        messages.success(request, "Welcome! You will need to complete \
                         your profile information before you're visible to other users!")
        return render(request, 'users/edit_profile.html')

    return render(request, 'users/dashboard.html', context)


@verified_email_required
def edit_profile(request):

    if request.method == 'POST':
        form = EditProfileForm(
            request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Your changes have been saved!")
            return redirect('account_dashboard')
        else:
            messages.error(
                request, "Form could not be submitted, please try again!")

    return render(request, 'users/edit_profile.html')


@verified_email_required
@never_cache
def all_users(request):
    """
    Return all users to the page and search if there is an ajax search request.
    """
    
    inds_to_exclude = ["None selected - please complete your profile", "All"]
    
    all_users = MyAccount.objects.all().exclude(
        pk=request.user.pk).exclude(first_name="").exclude(
            profile_completed=False).exclude(show_profile=False).exclude(
                industry__in=inds_to_exclude)
    free_account = request.user.package_tier == 1
    users_friends = Friend.objects.friends(request.user)
    friends_emails = []

    # Map friends to string of emails
    for i in users_friends:
        friends_emails.append(i.email)

    # For free account tier, locked by industry only
    if free_account:
        all_users = MyAccount.objects.filter(
            industry=request.user.industry).exclude(pk=request.user.pk).exclude(
                industry__in=inds_to_exclude)

    query = Q(to_user=request.user) | Q(from_user=request.user)
    user_friend_requests = FriendshipRequest.objects.filter(query)

    if request.is_ajax and request.method == "POST":
        query = request.POST['user_search']
        
        connections_only = request.POST.get('connections_only')
        if not free_account or request.user.is_admin:
            industry_query = request.POST['industry']
        else:
            industry_query = request.user.industry

        if query != "":
            queries = Q(first_name__icontains=query) | Q(last_name__icontains=query) | Q(
                description__icontains=query) | Q(location__icontains=query) | Q(
                job_role__icontains=query) | Q(skills__icontains=query)
        elif industry_query == "All":
            queries = ~Q(industry=industry_query)
        else:
            queries = Q(industry=industry_query)

        if free_account:
            query_results = MyAccount.objects.filter(
                industry=request.user.industry).exclude(pk=request.user.pk).exclude(
                    industry__in=inds_to_exclude)
        else:
            query_results = MyAccount.objects.filter(queries).exclude(
                pk=request.user.pk).exclude(first_name="").exclude(
                    industry__in=inds_to_exclude)

        if connections_only:
            results = query_results.filter(email__in=friends_emails)
        else:
            results = query_results

        context = {
            'search_results': results,
            'pending_friend_reqs': user_friend_requests,
            'free_account': free_account,
            'users_friends': friends_emails,
        }
        payload = render_to_string(
            'users/includes/ajax_user_search_results.html', context)
        return HttpResponse(json.dumps(payload), content_type="application/json")

    context = {
        'users': all_users,
        'pending_friend_reqs': user_friend_requests,
        'free_account': free_account,
        'users_friends': friends_emails,
    }

    return render(request, 'users/all_user_list.html', context)


@ verified_email_required
def dashboard_my_orders(request):

    stripe_pk = settings.STRIPE_PUBLIC_KEY
    stripe_sk = settings.STRIPE_SECRET_KEY
    stripe.api_key = stripe_sk

    user = MyAccount.objects.get(email=request.user)
    stripe_customer_id = user.stripe_customer_id

    if stripe_customer_id:

        invoices = stripe.Invoice.list(
            limit=10,
            customer=stripe_customer_id)

        upcoming_invoice = stripe.Invoice.upcoming(
            customer=stripe_customer_id,
        )
        
        customer_pm = stripe.Customer.retrieve(
            stripe_customer_id
        ).invoice_settings.default_payment_method
        
        if customer_pm != "null":
            has_pm = True
        else:
            has_pm = False
            
            
        up_inv_period = upcoming_invoice.lines.data[0].period
        package_id = upcoming_invoice.lines.data[0].price.id
        get_package_object = Package.objects.get(stripe_price_id=package_id)

        upcoming_invoice_dict = {
            "date": datetime.fromtimestamp(
                upcoming_invoice.created).strftime('%d %b %y'),
            "balance": upcoming_invoice.amount_due / 100,
            "period_start": datetime.fromtimestamp(up_inv_period.start).strftime(
                '%d %b %y'),
            "period_end": datetime.fromtimestamp(up_inv_period.end).strftime(
                '%d %b %y'),
            "package": get_package_object
        }

        invoice_list = []

        for i in invoices:

            if i.paid != False:
                period = i.lines.data[0].period
                invoice_date = datetime.fromtimestamp(i.created).strftime(
                    '%d %b %y')
                start_date = datetime.fromtimestamp(period.start).strftime(
                    '%d %b %y')
                end_date = datetime.fromtimestamp(period.end).strftime(
                    '%d %b %y')
                invoice_data = {
                    "order_id": i.metadata,
                    "invoice_date": invoice_date,
                    "date_start": start_date,
                    "date_end": end_date,
                    "amount": i.total / 100,
                    "download_url": i.invoice_pdf
                }
                invoice_list.append(invoice_data)
    
        context = {
            'invoices': invoice_list,
            'upcoming_invoice': upcoming_invoice_dict,
            'stripe_public_key': stripe_pk,
            'has_pm': has_pm,
        }
        return render(request, 'users/user_orders.html', context)

    else:

        context = {
            'invoices': None,
        }

    return render(request, 'users/user_orders.html', context)


def send_user_message(request):

    if request.method == "POST":

        # Verify users are friends before sending the message
        sender = request.user
        receiver_id = int(request.POST.get('receiver'))
        receiver_email = MyAccount.objects.get(pk=receiver_id)
        both_users_friends = Friend.objects.are_friends(
            request.user, receiver_email)

        if both_users_friends:
            # Clear previous messages
            storage = messages.get_messages(request)
            storage.used = True

            subject = f'You have a new message from {receiver_email.first_name} {receiver_email.last_name}'
            message = request.POST.get('message')

            email = EmailMessage(
                subject,
                message,
                sender,
                [receiver_email],
                reply_to=[sender],
            )
            email.send()

            messages.success(
                request, "Your message has been sent successfully!")
            return redirect('all_users')
        else:
            messages.error(
                request, "Your message could not be sent, please try again or contact us if the problem persists!")
            return redirect('all_users')

    return render(request, 'users/all_user_list.html')


""" AJAX REQUESTS """
# Connection functions using AJAX


@verified_email_required
def add_friend(request, **kwargs):
    """ Add a friend to this user's friend list with Ajax """
    if request.is_ajax and request.method == "GET":
        other_user = kwargs.get('other_user')
        other_user_pk = MyAccount.objects.get(pk=other_user)
        Friend.objects.add_friend(request.user, other_user_pk)
        return JsonResponse({"response": "Connection Requested Successfully",
                             "buttonId": other_user,
                             "type": "add"})


@verified_email_required
def cancel_friend(request, **kwargs):
    """ Cancel a pending request sent from user """
    if request.is_ajax and request.method == "GET":
        other_user = kwargs.get('other_user')
        other_user_pk = MyAccount.objects.get(pk=other_user)

        # Cancel the request
        FriendshipRequest.objects.get(to_user=other_user_pk).cancel()

        return JsonResponse({"response": "Connection Cancelled Successfully",
                             "buttonId": other_user,
                            "type": "cancel"})


@verified_email_required
def accept_friend(request, **kwargs):
    """ Accept an incoming pending request to this user """
    if request.is_ajax and request.method == "GET":
        other_user = kwargs.get('other_user')

        # Accept the request
        try:
            FriendshipRequest.objects.get(
                to_user=request.user, from_user=other_user).accept()
        except:
            messages.error(request,
                           "We could no longer find this request. Please refresh the page and try again")

        return JsonResponse({"response": "Connection Accepted Successfully",
                             "buttonId": other_user,
                            "type": "accept"})


@verified_email_required
def decline_friend(request, **kwargs):
    """ Decline an incoming pending request to this user """
    if request.is_ajax and request.method == "GET":
        other_user = kwargs.get('other_user')
        other_user_pk = MyAccount.objects.get(pk=other_user)

        # Decline the request
        try:
            FriendshipRequest.objects.get(
                to_user=request.user, from_user=other_user).reject()
        except:
            messages.error(request,
                           "We could no longer find this request. Please refresh the page and try again")

        return JsonResponse({"response": "Connection Declined Successfully",
                             "buttonId": other_user,
                            "type": "decline"})


@verified_email_required
def remove_friend(request, **kwargs):
    """ Remove an existing friend of this user """
    if request.is_ajax and request.method == "GET":
        other_user = kwargs.get('other_user')
        other_user_pk = MyAccount.objects.get(pk=other_user)

        # Get both initial and reverse of friendship
        get_connection_primary = Friend.objects.filter(
            to_user=request.user).filter(from_user=other_user_pk)[0]
        get_connection_secondary = Friend.objects.filter(
            to_user=other_user_pk).filter(from_user=request.user)[0]

        # Remove the friend objects
        try:
            get_connection_primary.delete()
            get_connection_secondary.delete()
            friend_list.remove(other_user_pk)

        except Exception as e:
            messages.error(request,
                           "We could no longer find this request. Please refresh the page and try again")

        return JsonResponse({"response": "Connection Removed Successfully",
                             "buttonId": other_user,
                            "type": "remove"})
