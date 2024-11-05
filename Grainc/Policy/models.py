from django.db import models
import django.utils

# Create your models here.
class CompanyPolicy(models.Model):
    create_date = models.DateField(default=django.utils.timezone.now)
    policy_content = models.TextField()

class PrivacyPolicy(models.Model):
    create_date = models.DateField(default=django.utils.timezone.now)
    policy_content = models.TextField()

