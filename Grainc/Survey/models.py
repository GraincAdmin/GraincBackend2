from django.db import models
from django.utils import timezone
# Create your models here.


class Survey(models.Model):
    user_email = models.CharField(max_length=100)
    create_date = models.DateTimeField(default=timezone.now)
    title = models.CharField(max_length=100)
    detail = models.TextField(blank=True, null=True)  

        # 리텐션 주기를 나타cur내는 필드 추가
    SURVEY_TYPE = [
        ('account_cancel', 'Account_Cancel'),
    ]
    
    survey_type = models.CharField(
        max_length=50,
        choices=SURVEY_TYPE,
    )


    