from .models import Notification
from AuthUser.models import UserFCMToken

from rest_framework import serializers
from Grainc.Global_Function.ContentDataFormatter import create_date_formatter
from django.contrib.humanize.templatetags.humanize import intcomma


class NotificationDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ('id',
                  'create_date', 
                  'notification_type',
                  'notification_create_user', 
                  'notification_article', 
                  'notification_comment',
                  'notification_comment_reply',
                  'notification_donation',
                  'notification_donation_withdrawal',
                  'notification_inquiry',
                  'notification_announcement'
                )
        
    def to_representation(self, instance):
        data = super().to_representation(instance)
        # Basic Information
        data['formatted_create_date'] = create_date_formatter(instance.create_date)

        if instance.notification_create_user:
            data['author_username'] = instance.notification_create_user.username
            if instance.notification_create_user.profile_image:
                data['author_profile_image'] = instance.notification_create_user.profile_image.url

        # Article Notification
        if instance.notification_article:
            data['content_id'] = instance.notification_article.id
            data['notification_subject'] = instance.notification_article.subject
            data['notification_type'] = 'article'

        # Comment Notification
        if instance.notification_comment:
            # content id replaced with article id
            data['content_id'] = instance.notification_comment.article.id 
            data['comment_count'] = intcomma(instance.notification_comment.article.comments)
            data['notification_subject'] = f'{instance.notification_comment.author.username}이 댓글을 작성했습니다'
            data['notification_type'] = 'comment'

        # Reply Notification
        if instance.notification_comment_reply:
            # content id replaced with article id
            data['content_id'] = instance.notification_comment_reply.reply_comment.article.id
            data['comment_count'] = intcomma(instance.notification_comment_reply.reply_comment.article.comments)
            data['notification_subject'] = f'{instance.notification_comment_reply.author.username}이 답글을 작성했습니다'
            data['notification_type'] = 'comment_reply'
            
        # Donation Notification
        if instance.notification_donation:
            data['content_id'] = instance.notification_donation.id
            data['notification_subject'] = f'{instance.notification_donation.donator.username}이 후원했습니다'
            data['notification_type'] = 'donation'

        # Donation Withdrawal Notification
        if instance.notification_donation_withdrawal:
            data['content_id'] = instance.notification_donation_withdrawal.id
            data['notification_subject'] = '후원금 출금결과 알림'
            data['notification_type'] = 'donation_withdrawal'

        # Inquiry Notification
        if instance.notification_inquiry:
            data['content_id'] = instance.notification_inquiry.id
            data['notification_subject'] = '문의 답변이 도착했습니다'
            data['notification_type'] = 'inquiry'

        # Announcement Notification
        if instance.notification_announcement:
            data['content_id'] = instance.notification_announcement.id
            data['notification_subject'] = instance.notification_announcement.subject
            data['notification_type'] = 'announcement'

        return data
        

class FCMTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserFCMToken
        fields = ['is_push_notification', 'is_article_notification', 
                  'is_comment_notification', 'is_comment_reply_notification', 
                  'is_donation_notification', 'is_donation_withdrawal_notification', 
                  'is_announcement_notification', 'is_inquiry_notification']
        
