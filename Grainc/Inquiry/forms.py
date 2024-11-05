from django import forms
from .models import Inquiry

class InquiryForm(forms.ModelForm):
    class Meta:
        model = Inquiry
        fields = ('User',
                  'Inquiry_type',
                  'Inquiry_subject',
                  'Inquiry_main_content')
        
        