from django import forms
from .models import ServiceUser
import string
import random

class SellReportsUserCreationForm(forms.ModelForm):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)
    
    class Meta:
        model = ServiceUser
        fields = ('email', 'username')

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user
    

def generate_random_password(length=12):
    characters = string.ascii_letters + string.digits
    password = ''.join(random.choice(characters) for i in range(length))
    return password

class SellReportsSocialAccountCreationFrom(forms.ModelForm):
    class Meta:
        model = ServiceUser
        fields = ('email', 'social_account_provider', 'social_account_detail')


    def social_account_setup(self, commit=True):
        user = super().save(commit=False)
        user.is_social_account = True
        user.social_account_provider = self.cleaned_data['social_account_provider']
        user.social_account_detail = self.cleaned_data['social_account_detail']
        user.set_password(generate_random_password())
        user.is_active = True
        if commit:
            user.save()
        return user

