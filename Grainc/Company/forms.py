from django import forms
from . models import Company_Announcement

class Company_Announcement_Form(forms.ModelForm):

    class Meta:
        model = Company_Announcement
        fields = ['Company_Announcement_Date', 'Company_Announcement_Subject', 'Company_Announcement_Content']

