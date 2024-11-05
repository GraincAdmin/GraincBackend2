from django import forms

from .models import CompanyPolicy, PrivacyPolicy



class SellReportsCompanyPolicy_Form(forms.ModelForm):

    class Meta:
        model = CompanyPolicy
        fields = ('create_date', 'policy_content')


class SellReportsPrivacyPolicy_Form(forms.ModelForm):

    class Meta:
        model = PrivacyPolicy
        fields = ('create_date', 'policy_content')
