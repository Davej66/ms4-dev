from django.shortcuts import render
from users.forms import ProfileForm


def account_dashboard(request):

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

    return render(request, 'users/dashboard.html')
