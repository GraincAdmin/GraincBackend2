from django import forms
#Announcement
from .models import Notification

class NotificationForm(forms.ModelForm):

    class Meta:
        model = Notification
        fields = (
            'notification_type',
            'notification_create_user',
            'receivers',

            # notification models
            'notification_article', 
            'notification_comment',
            'notification_comment_reply',
            'notification_donation',
            'notification_donation_withdrawal',
            'notification_inquiry',
            'notification_announcement'
        )