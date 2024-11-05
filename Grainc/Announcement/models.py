from django.db import models
import django.utils

# Create your models here.

class Announcement(models.Model):
    create_date = models.DateTimeField(default=django.utils.timezone.now)
    subject = models.CharField(max_length=1000)
    content = models.TextField()
    start_time = models.DateTimeField(blank=True, null=True)
    end_time = models.DateTimeField(blank=True, null=True)
    is_important = models.BooleanField(default=False)
    
