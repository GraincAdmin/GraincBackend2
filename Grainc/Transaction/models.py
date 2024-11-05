from django.db import models
import django.utils
from django.conf import settings

from Community.models import Community_Articles

    
class Membership_Article_Donation_Record(models.Model):
    article = models.ForeignKey(Community_Articles, on_delete=models.SET_NULL, null=True)
    donator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    amount = models.PositiveIntegerField()
    donation_date = models.DateTimeField(default=django.utils.timezone.now)
    

class Membership_Donation_Withdrawal_Request(models.Model):
    request_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    request_date = models.DateTimeField(default=django.utils.timezone.now)
    amount = models.PositiveIntegerField()

    # Bank Information
    account_holder = models.CharField(max_length=100)
    bank = models.CharField(max_length=100)
    bank_code = models.CharField(max_length=100)
    bank_account = models.CharField(max_length=100)


    waiting = 'waiting'
    completed = 'completed'
    failed = 'failed'

    STATUS_TYPE_CHOICES = [
        (waiting, '정산대기'),
        (completed, '정산완료'),
        (failed, '정산거부 (1:1문의 해주세요)'),
    ]

    # Status field
    status = models.CharField(
        max_length=20,  # Ensure to specify max_length
        choices=STATUS_TYPE_CHOICES,
        default=waiting  # Set the default value directly
    )

    rejection_message = models.TextField(blank=True, null=True)

    # For Backup
    request_user_email = models.CharField(max_length=100)


