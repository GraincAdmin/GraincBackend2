from django.db import models
import django.utils
from django.conf import settings
# Notification Forming models
from Community.models import Community_Articles, Community_Article_Comment, Community_Article_Comment_Reply
from Transaction.models import Membership_Article_Donation_Record, Membership_Donation_Withdrawal_Request
from Announcement.models import Announcement
from Inquiry.models import Inquiry
# Create your models here.
class Notification(models.Model):
    create_date = models.DateTimeField(default=django.utils.timezone.now)

    ARTICLE = 'article'
    COMMENT = 'comment'
    COMMENT_REPLY = 'comment_reply'
    DONATION = 'donation'
    DONATION_WITHDRAWAL = 'donation_withdrawal'
    INQUIRY = 'inquiry'
    ANNOUNCEMENT = 'announcement'

    
    NOTIFICATION_TYPE_CHOICES = [
        (ARTICLE, 'Article'),
        (COMMENT, 'Comment'),
        (COMMENT_REPLY, 'CommentReply'),
        (DONATION, 'Donation'),
        (DONATION_WITHDRAWAL, 'DonationWithdrawal'),
        (INQUIRY, 'Inquiry'),
        (ANNOUNCEMENT, 'Announcement'),
    ]

    notification_type = models.CharField(
        max_length=20,  # Ensure to specify max_length
        choices=NOTIFICATION_TYPE_CHOICES
    )
    notification_create_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications_created')
    receivers = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='notifications_received', blank=True)
    notification_on_read = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='received_notification')
    notification_on_delete = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='notification_deleted_user')

    # notification models
    notification_article = models.ForeignKey(Community_Articles, on_delete=models.CASCADE, null=True, blank=True)
    notification_comment = models.ForeignKey(Community_Article_Comment, on_delete=models.CASCADE, null=True, blank=True)
    notification_comment_reply = models.ForeignKey(Community_Article_Comment_Reply, on_delete=models.CASCADE, null=True, blank=True)
    notification_donation = models.ForeignKey(Membership_Article_Donation_Record, on_delete=models.CASCADE, null=True, blank=True)
    notification_donation_withdrawal = models.ForeignKey(Membership_Donation_Withdrawal_Request, on_delete=models.CASCADE, null=True, blank=True)
    notification_inquiry = models.ForeignKey(Inquiry, on_delete=models.CASCADE, null=True, blank=True)
    notification_announcement = models.ForeignKey(Announcement, on_delete=models.CASCADE, null=True, blank=True)

    # notification sent
    is_sent = models.BooleanField(default=False)
