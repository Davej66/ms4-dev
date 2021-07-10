from django.shortcuts import render
from users.forms import ProfileForm
from allauth.account.decorators import verified_email_required
from users.models import MyAccount


@verified_email_required
def account_dashboard(request):

    user = MyAccount.objects.get(email=request.user)
    full_name = user.first_name + " " + user.last_name
    user_package = user.package_name
    print(request.user)
    if request.method == "POST":
        form_data = {
            "first_name": "bradley",
            "last_name": "cooney",
            "job_role": "producer",
        }

        profile_form = ProfileForm(form_data, instance=request.user)
        print(profile_form.errors)
        if profile_form.is_valid():
            profile_form.save()
            print("saved: ", form_data)

    context = {
        'full_name': full_name.title(),
        'package': user_package,
    }

    return render(request, 'users/dashboard.html', context)
