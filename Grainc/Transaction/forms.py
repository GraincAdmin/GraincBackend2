from django import forms
from .models import Membership_Article_Donation_Record
from .models import Membership_Donation_Withdrawal_Request

# Membership 

class MembershipDonationRecordFrom(forms.ModelForm):
    class Meta:
        model = Membership_Article_Donation_Record
        fields = ['article', 'donator', 'amount']

class MembershipDonationWithdrawalRequestFrom(forms.ModelForm):
    class Meta:
        model = Membership_Donation_Withdrawal_Request
        fields = [
            'request_user', 
            'amount', 
            'account_holder', 
            'bank', 
            'bank_code', 
            'bank_account', 
            'request_user_email'
        ]
        