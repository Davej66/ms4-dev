from django.conf import settings
from django.shortcuts import get_object_or_404
from users.models import MyAccount

def user_context(request):
    try:
        this_user = MyAccount.objects.get(email=request.user)
        full_name = this_user.first_name + " " + this_user.last_name
        full_name_title = full_name.title()

        context = {
            'this_user': this_user,
            'profile_image': this_user.profile_image.url,
            'full_name': full_name_title
        }
        print("session context", context)
        return context
    except Exception as e:
        context = {
            'this_user': "Anonymous",
            'profile_image': "",
            'full_name': ""
        }
        return context
