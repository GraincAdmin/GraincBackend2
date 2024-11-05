from rest_framework import serializers
from django.utils.html import strip_tags
from django.utils.safestring import mark_safe
from django.template.defaultfilters import floatformat
from django.contrib.humanize.templatetags.humanize import intcomma
from datetime import timedelta
from django.utils import timezone

from .models import Membership_Article_Donation_Record
from .models import Membership_Donation_Withdrawal_Request


"""
Donation record for better approach
"""
 
class MembershipDonationRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = Membership_Article_Donation_Record
        fields = ('id', 'article', 'amount', 'donation_date')

    def to_representation(self, instance):
        data = super().to_representation(instance)
        try:
            data['formatted_donation_amount'] = intcomma(instance.amount)
            data['article_subject'] = instance.article.subject
            data['formatted_donated_date'] = instance.donation_date.strftime("%Y.%m.%d %H:%M")
        except Exception as e:
            return
        return data
    

"""
Donation Withdrawal Record 
"""

class MembershipDonationWithdrawalSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Membership_Donation_Withdrawal_Request
        fields = ('id', 'request_date', 'amount', 'status')

    def to_representation(self, instance):
        data = super().to_representation(instance)
        try:
            data['formatted_request_date'] = instance.request_date.strftime("%Y.%m.%d %H:%M")
            data['formatted_withdrawal_amount'] = intcomma(instance.amount)
        except Exception as e:
            return
        return data

class MembershipDonationWithdrawalDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Membership_Donation_Withdrawal_Request
        fields = (
            'id', 
            'request_date', 
            'amount',
            'account_holder',
            'bank',
            'bank_account',
            'status',
            'rejection_message'
        )

    def to_representation(self, instance):
        data = super().to_representation(instance)
        try:
            data['formatted_request_date'] = instance.request_date.strftime("%Y.%m.%d %H:%M")
            data['formatted_withdrawal_amount'] = intcomma(instance.amount)
        except Exception as e:
            return
        return data
    
