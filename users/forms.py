from django import forms
from .models import MyAccount


class ProfileForm(forms.ModelForm):
    class Meta:
        model = MyAccount
        fields = ('first_name', 'last_name', 'job_role')


class UpdateUserPackage(forms.ModelForm):
    class Meta:
        model = MyAccount
        fields = ('package_tier','package_name')