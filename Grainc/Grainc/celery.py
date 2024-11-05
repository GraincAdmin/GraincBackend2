# celery.py

import os
from celery import Celery
from celery.schedules import crontab, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Grainc.settings')

app = Celery('Grainc')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

# Define the periodic task
app.conf.beat_schedule = {
    'delete-old-notifications-every-hour': {
        'task': 'Notification.tasks.delete_old_notifications',
        'schedule': timedelta(minutes=1)
    },
    
    # Company Statistic Calculation
    'calculate-company-retention': {
        'task': 'Statistics.tasks.calculate_seven_day_retention',
        'schedule': crontab(hour=3, minute=0),  # 매일 새벽 3시
    },

    # Company Revenue Calculation 
    'calculate_company_revenue': {
        'task': 'Statistics.tasks.calculate_daily_revenue',
        'schedule': timedelta(minutes=1)
    }
}

app.conf.broker_connection_retry_on_startup = True
