from rest_framework import serializers
from django.utils.safestring import mark_safe
from .models import CompanyPolicy, PrivacyPolicy

class CompanyPolicySerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyPolicy
        fields = '__all__' 
    
    def to_representation(self, initial):
        data = super().to_representation(initial)
        data['policy_id'] = initial.id
        data['formatted_policy_content'] = mark_safe(initial.policy_content)
        return data

class CompanyPolicySelectorSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyPolicy
        fields = ('create_date',)

    def to_representation(self, initial):
        data = super().to_representation(initial)
        data['policy_id'] = initial.id
        return data


class PrivacyPolicySerializer(serializers.ModelSerializer):
    class Meta:
        model = PrivacyPolicy
        fields = '__all__' 
    
    def to_representation(self, initial):
        data = super().to_representation(initial)
        data['policy_id'] = initial.id
        data['formatted_policy_content'] = mark_safe(initial.policy_content)
        return data

class PrivacyPolicySelectorSerializer(serializers.ModelSerializer):
    class Meta:
        model = PrivacyPolicy
        fields = ('create_date',)

    def to_representation(self, initial):
        data = super().to_representation(initial)
        data['policy_id'] = initial.id
        return data
