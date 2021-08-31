from django import forms
from .models import Event

class CreateEventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ('title', 'description', 'header_image',
            'industry', 'location', 'start_datetime', 'end_datetime', 
            'timezone', 'max_reg')


class EditEventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ('title', 'description', 'header_image','location', 'max_reg')
    