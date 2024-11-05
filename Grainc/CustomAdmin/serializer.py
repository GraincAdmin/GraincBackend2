from django.utils.html import strip_tags
from django.utils.safestring import mark_safe
from rest_framework import serializers
from django.utils import timezone

# Global Function 
from Grainc.Global_Function.ContentDataFormatter import create_date_formatter

# CustomAdmin Required Models
from Inquiry.models import Inquiry
from AuthUser.models import ServiceUser
from Community.models import Community_Articles, ReportedArticlesComments
from Announcement.models import Announcement
from Policy.models import CompanyPolicy, PrivacyPolicy
from Company.models import Company_Announcement
from Transaction.models import Membership_Article_Donation_Record, Membership_Donation_Withdrawal_Request
from Survey.models import Survey
from Statistics.models import CompanyRevenueStatistics

# Inquiry management

class InquirySimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Inquiry
        fields = ('id', 'Inquiry_subject', 'Inquiry_type', 'Inquiry_date', 'is_replied')

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['formatted_date'] = instance.Inquiry_date.strftime('%Y.%m.%d:%H.%M.%S')
        return data
    
class InquiryDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Inquiry
        fields = ('Inquiry_subject', 'Inquiry_main_content', 'Inquiry_reply', 'User', 'is_replied')

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['formatted_main_content'] = mark_safe(instance.Inquiry_main_content)
        data['formatted_reply'] = mark_safe(instance.Inquiry_reply)
        data['author_username'] = instance.User.username
        return data

# User management

class UserManagementSerializerSimple(serializers.ModelSerializer):
    class Meta:
        model = ServiceUser
        fields = ('username', 'email', 'id', 'is_membership')

class UserManagementSerializerDetail(serializers.ModelSerializer):
    class Meta:
        model = ServiceUser
        fields = (
            'username', 
            'email', 
            'is_active', 
            'is_admin', 
            'is_membership',
            'membership_donation_cash',
            'community_restriction',
            'violation_detail_community',
        )

# Community Management

class AdminCommunityManagementSimple(serializers.ModelSerializer):
    class Meta:
        model = Community_Articles
        fields = ( 'id', 'author', 'category', 'sub_category','subject', 'is_membership')
    def to_representation(self, instance):
        data = super().to_representation(instance)
        if instance.author:
            data['author_username'] = instance.author.username
        else:
            data['author_username'] = '탈퇴유저'
        return data
    
class AdminCommunityManagementDetail(serializers.ModelSerializer):
    class Meta:
        model = Community_Articles
        fields = ('author', 
                  'category', 
                  'create_date',
                  'subject',
                  'sub_category',
                  'images',
                  'saved_article',
                  'is_hidden_admin',
                  'is_membership'
                )
    def to_representation(self, instance):
        data = super().to_representation(instance)
        if (instance.author):
            data['author_username'] = instance.author.username
        else:
            data['author_username'] = '유저정보 없음'
        return data

# Violation

class ReportedArticlesCommentsSimple(serializers.ModelSerializer):
    class Meta:
        model = ReportedArticlesComments
        fields = ('id', 'reported_user', 'type', 'create_date', 'is_task_done')

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if instance.reported_user:
            data['reported_user_username'] = instance.reported_user.username
        data['formatted_date'] = create_date_formatter(instance.create_date)
        return data

class ReportedArticlesCommentsDetail(serializers.ModelSerializer):
    class Meta:
        model = ReportedArticlesComments
        fields = ('reported_article', 'reported_comment', 'reported_comment_reply', 'reported_user', 'type', 'detail')

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if instance.reported_user:
            data['reported_user_username'] = instance.reported_user.username
        else:
            data['reported_user_username'] = '유저정보 없음'

        if instance.reported_article:
            data['content_type'] = 'article'
            data['violated_user_username'] = instance.reported_article.author.username
        elif instance.reported_comment:
            data['content_type'] = 'comment'
            data['violated_user_username'] = instance.reported_comment.author.username
        elif instance.reported_comment_reply:
            data['content_type'] = 'reply'
            data['violated_user_username'] = instance.reported_comment_reply.author.username
        else:
            data['content_type'] = '알 수 없음'
            data['violated_user_username'] = '유져정보 없음'

        data['formatted_date'] = create_date_formatter(instance.create_date)
        return data

# membership donation record

class DonationRecordSimple(serializers.ModelSerializer):
    class Meta:
        model = Membership_Article_Donation_Record
        fields = ('id', 'article', 'donator', 'amount', 'donation_date')

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['formatted_donation_date'] = create_date_formatter(instance.donation_date)
        if instance.donator:
            data['donator_username'] = instance.donator.username
        else:
            data['donator_username'] = '유저정보 없음'

        if instance.article:
            data['article_subject'] = instance.article.subject
        else:
            data['article_subject'] = '게시글 정보 없음'

        return data
    
class DonationRecordDetail(serializers.ModelSerializer):
    class Meta:
        model = Membership_Article_Donation_Record
        fields = ('id', 'article', 'donator', 'amount', 'donation_date')

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['formatted_donation_date'] = create_date_formatter(instance.donation_date)
        if instance.donator:
            data['donator_username'] = instance.donator.username
        else:
            data['donator_username'] = '유저정보 없음'

        if instance.article:
            data['article_subject'] = instance.article.subject
            if instance.article.author:
                data['article_author_username'] = instance.article.author.username
            else:
                data['article_author_username'] = '유저정보 없음'
        else:
            data['article_subject'] = '게시글 정보 없음'
            data['article_author_username'] = '유저정보 없음'
        

        return data

# Membership Donation Withdrawal Request

class MembershipDonationWithdrawalRecordSimple(serializers.ModelSerializer):
    class Meta:
        model = Membership_Donation_Withdrawal_Request
        fields = ('id', 'request_user', 'amount', 'request_date', 'status')

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['formatted_request_date'] = instance.request_date.strftime('%Y.%m.%d:%H.%M.%S')
        if instance.request_user:
            data['request_user_username'] = instance.request_user.username
        else:
            data['request_user_username'] = '유저정보 없음'

        return data

class MembershipDonationWithdrawalRecordDetail(serializers.ModelSerializer):
    class Meta:
        model = Membership_Donation_Withdrawal_Request
        fields = ('id', 'request_user', 'amount', 'request_date', 
                  'account_holder', 'bank', 'bank_code', 'bank_account',
                  'status', 'rejection_message'
                )

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['formatted_request_date'] = instance.request_date.strftime('%Y.%m.%d:%H.%M.%S')
        if instance.request_user:
            data['request_user_username'] = instance.request_user.username
        else:
            data['request_user_username'] = '유저정보 없음' 

        return data
    

# Company Announcement

class AdminCompanyAnnouncementSerializerSimple(serializers.ModelSerializer):
    class Meta:
        model = Announcement
        fields = ('id' ,'subject', 'create_date')

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['formatted_date'] = instance.create_date.strftime('%Y.%m.%d:%H.%M.%S')
        return data
    
class AdminCompanyAnnouncementSerializerDetail(serializers.ModelSerializer):
    class Meta:
        model = Announcement
        fields = ('subject', 'content', 'start_time', 'end_time', 'is_important')

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['formatted_content'] = strip_tags(instance.content)
        data['start_time'] = instance.start_time.isoformat() if instance.start_time else None
        data['end_time'] = instance.end_time.isoformat() if instance.end_time else None
        return data

# Company Policy

class AdminCompanyPolicySerializerSimple(serializers.ModelSerializer):
    class Meta:
        model = CompanyPolicy
        fields = ('id', 'create_date' )

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['formatted_date'] = instance.create_date.strftime('%Y.%m.%d:%H.%M.%S')
        return data
    
class AdminCompanyPolicySerializerDetail(serializers.ModelSerializer):
    class Meta:
        model = CompanyPolicy
        fields = ('policy_content', )


class AdminPrivacyPolicySerializerSimple(serializers.ModelSerializer):
    class Meta:
        model = PrivacyPolicy
        fields = ('id', 'create_date')

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['formatted_date'] = instance.create_date.strftime('%Y.%m.%d:%H.%M.%S')
        return data
    
class AdminPrivacyPolicySerializerDetail(serializers.ModelSerializer):
    class Meta:
        model = PrivacyPolicy
        fields = ('policy_content', )
    

# Company Announcement

class AdminLTDAnnouncementSerializerSimple(serializers.ModelSerializer):
    class Meta:
        model = Company_Announcement
        fields = ( 'id', 'Company_Announcement_Subject', 'Company_Announcement_Date')
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['formatted_date'] = instance.Company_Announcement_Date.strftime('%Y.%m.%d:%H.%M.%S')
        return data
    

class AdminLTDAnnouncementSerializerDetail(serializers.ModelSerializer):
    class Meta:
        model = Company_Announcement
        fields = ('Company_Announcement_Subject', 'Company_Announcement_Content')
    

# Survey

class AdminSurveySerializerSimple(serializers.ModelSerializer):
    class Meta:
        model = Survey
        fields = ('id' ,'user_email', 'create_date', 'survey_type')

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['create_date'] = create_date_formatter(instance.create_date)
        if instance.survey_type == 'account_cancel':
            data['type'] = '회원탈퇴'
        else:
            data['type'] = ''
        return data
    
class AdminSurveySerializerDetail(serializers.ModelSerializer):
    class Meta:
        model = Survey
        fields = ('user_email', 'create_date', 'title', 'detail')

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['create_date'] = instance.create_date.strftime('%Y.%m.%d:%H.%M.%S')
        return data
    


# PO Performance

class AdminRevenueSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyRevenueStatistics
        fields = ('combined_revenue_data', )

    def to_representation(self, instance):
        data = super().to_representation(instance)
        return data