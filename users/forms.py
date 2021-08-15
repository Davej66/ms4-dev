from django import forms
from .models import MyAccount
import random

# Allauth form customisation tutorial from Gavin Wiener at Medium:
# https://gavinwiener.medium.com/modifying-django-allauth-forms-6eb19e77ef56

class RegistrationForm(forms.ModelForm):
    """
    Add additional fields to the standard Allauth signup form.
    """
    field_order = ['first_name', 'last_name']

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        for fieldname, field in self.fields.items():
            field.widget.attrs.update({
                'class':'form_input',    
            })
            
        self.fields['first_name'].widget.attrs.update({
            'placeholder': 'Enter your first name'
        })
        
        self.fields['last_name'].widget.attrs.update({
            'placeholder': 'Enter your last name'
        })
        

    # Allauth custom password input code snippet for 'password1' from dirkgroten on SO:
    # https://stackoverflow.com/questions/48073923/django-allauth-custom-template-not-hashing-passwords
    class Meta:
        model = MyAccount
        fields = ('first_name', 'last_name')

    # Snippet below from 'Pennersr' in this StackOverflow thread: 
    # https://stackoverflow.com/questions/12303478/how-to-customize-user-profile-when-using-django-allauth
    def signup(self, request, user):
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.username = random.randint(10000,99999)
        user.save()


class EditProfileForm(forms.ModelForm):
    class Meta:
        model = MyAccount
        fields = ('first_name', 'last_name', 'job_role',
            'profile_image', 'skills', 'location', 'description', 
            'industry', 'email', 'show_profile', 'profile_completed')


class UpdateUserPackage(forms.ModelForm):
    class Meta:
        model = MyAccount
        fields = ('package_tier', 'package_name', 'stripe_customer_id')

class AddUserSubscription(forms.ModelForm):
    class Meta:
        model = MyAccount
        fields = ('stripe_subscription_id',)