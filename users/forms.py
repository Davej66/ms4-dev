from django import forms
from .models import MyAccount


class ProfileForm(forms.ModelForm):
    class Meta:
        model = MyAccount
        fields = ('first_name','last_name','job_role')