from django.db import models
import django.utils
# Create your models here.

class CompanyRevenueStatistics(models.Model):
    create_date = models.DateTimeField(default=django.utils.timezone.now)
    defined_revenue = models.PositiveIntegerField(default=0)
    combined_revenue_data = models.JSONField(blank=True, null=True)


class CompanyCarryingCapacity(models.Model):
    create_date = models.DateTimeField(default=django.utils.timezone.now)
    new_customers = models.PositiveIntegerField(default=0)

    # calculated based on MAU
    percentage_loss = models.PositiveIntegerField(default=0)

class CompanyRetention(models.Model):
    create_date = models.DateTimeField(default=django.utils.timezone.now)
    retention = models.FloatField(default=0)
    
    # 리텐션 주기를 나타cur내는 필드 추가
    RETENTION_PERIOD_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
    ]
    
    retention_period = models.CharField(
        max_length=10,
        choices=RETENTION_PERIOD_CHOICES,
        default='monthly'  # 기본값 설정
    )