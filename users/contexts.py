from django.conf import settings
from django.core.serializers import serialize
from django.contrib import messages
from django.shortcuts import get_object_or_404
from users.models import MyAccount, Skills, Roles

def user_context(request):

    skill_names = []

    try:
        this_user = MyAccount.objects.get(email=request.user)
        full_name = this_user.first_name + " " + this_user.last_name
        full_name_title = full_name.title()
        
        # Return all skills and user skills
        skills = Skills.objects.all()
        for skill in skills:
            skill_names.append(skill.skill_name)
        user_skills = this_user.skills
        print("user skills",user_skills)
        
        # Return all roles and user role
        roles = serialize('json', Roles.objects.all())

        context = {
            'this_user': this_user,
            'profile_image': this_user.profile_image.url,
            'full_name': full_name_title,
            'skills': skill_names,
            'user_skills': user_skills,
            'roles': roles,
        }
        return context
    except Exception as e:
        messages.error(request,
            f"There's been an error: {e}. We couldn't find the user you're looking for.")
        context = {
            'this_user': "Anonymous",
            'profile_image': "",
            'full_name': ""
        }
        return context
