from django.db import models
# Create your models here.
from django.conf import settings
import django.utils

# Create your models here.

class Inquiry(models.Model):
    Inquiry_date = models.DateTimeField(default=django.utils.timezone.now)
    User = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    Inquiry_type = models.CharField(max_length=50)
    Inquiry_subject = models.CharField(max_length=500)
    Inquiry_main_content = models.TextField()
    Inquiry_reply = models.TextField(blank=True, null=True)
    Inquiry_reply_date = models.DateTimeField(blank=True, null=True)
    is_replied = models.BooleanField(default=False)

