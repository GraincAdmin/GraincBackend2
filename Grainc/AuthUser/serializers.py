from .models import ServiceUser
from django.contrib.auth.password_validation import validate_password
from django.contrib.humanize.templatetags.humanize import intcomma
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.utils import timezone

#User Profile

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Frontend에서 더 필요한 정보가 있다면 여기에 추가적으로 작성하면 됩니다. token["is_superuser"] = user.is_superuser 이런식으로요.
        token['id'] = user.id
        token['username'] = user.username
        token['email'] = user.email
        token['is_admin'] = user.is_admin
        token['is_membership'] = user.is_membership
        print(token)
        print(user)
        user.last_active_date = timezone.now()
        user.save()
        return token
    

class GlobalUserInformationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceUser    
        fields = ('username', 'pk', 'profile_image')    

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['subscribing_status'] = True
        return data
    



# User Profile Serializer
class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceUser
        fields = ('username', 'likes_count', 'subscribers', 'profile_image', 'introduction', 'article_count')

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['subscribers_count'] = intcomma(instance.subscribers.count())
        data['user_profile_image'] = instance.profile_image.url
        data['article_count'] = intcomma(instance.article_count)
        return data
    
# My Page

# My Profile data Serializer
class MyPageProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceUser
        fields = ('introduction', 'donation_message')
