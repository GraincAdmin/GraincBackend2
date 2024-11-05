from django import forms
#Announcement
from .models import Announcement

class Announcement_Form(forms.ModelForm):

    class Meta:
        model = Announcement
        fields = ('create_date', 'subject', 'content', 'is_important', 'start_time', 'end_time')