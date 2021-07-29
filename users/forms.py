from django import forms
from .models import MyAccount


# Allauth form customisation tutorial from Gavin Wiener at Medium:
# https://gavinwiener.medium.com/modifying-django-allauth-forms-6eb19e77ef56

class RegistrationForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        for fieldname, field in self.fields.items():
            field.widget.attrs.update({
                'class':'form_input',    
            })
        self.fields['first_name'].widget.attrs.update({
            'class':'form_inputfirst',
        })

    class Meta:
        model = MyAccount
        fields = ('first_name', 'last_name', 'email', 'stripe_customer_id')


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