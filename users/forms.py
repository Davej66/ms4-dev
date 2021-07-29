from django import forms
from .models import MyAccount
from allauth.account.forms import SignupForm


# Allauth form customisation tutorial from Gavin Wiener at Medium:
# https://gavinwiener.medium.com/modifying-django-allauth-forms-6eb19e77ef56

class RegistrationForm(forms.ModelForm, SignupForm):
    
    field_order = ['first_name', 'last_name', 'email', 'password1']

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        for fieldname, field in self.fields.items():
            field.widget.attrs.update({
                'class':'form_input',    
            })
        self.fields['first_name'].widget.attrs.update({
            'class': 'half-input',
        })
        self.fields['last_name'].widget.attrs.update({
            'class':'half-input',
        })
        password1 = forms.CharField(label='Password', widget=forms.PasswordInput(attrs={'placeholder': 'Password:'}))

    # Allauth custom password input code snippet for 'password1' from dirkgroten on SO:
    # https://stackoverflow.com/questions/48073923/django-allauth-custom-template-not-hashing-passwords
    class Meta:
        model = MyAccount
        fields = ('first_name', 'last_name', 'email')
    
    



class ProfileForm(forms.ModelForm):
    class Meta:
        model = MyAccount
        fields = ('first_name', 'last_name', 'job_role')


class UpdateUserPackage(forms.ModelForm):
    class Meta:
        model = MyAccount
        fields = ('package_tier', 'package_name', 'stripe_customer_id')

class AddUserSubscription(forms.ModelForm):
    class Meta:
        model = MyAccount
        fields = ('stripe_subscription_id',)