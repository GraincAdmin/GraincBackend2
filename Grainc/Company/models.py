from django.db import models
import django.utils

# Create your models here.
class Company_Announcement(models.Model):
    Company_Announcement_Date = models.DateTimeField(default=django.utils.timezone.now)
    Company_Announcement_Subject = models.CharField(max_length=255)
    Company_Announcement_Content = models.TextField()