# Generated by Django 5.1.3 on 2024-11-05 09:25

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('Community', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Membership_Article_Donation_Record',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.PositiveIntegerField()),
                ('donation_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('article', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='Community.community_articles')),
                ('donator', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Membership_Donation_Withdrawal_Request',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('request_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('amount', models.PositiveIntegerField()),
                ('account_holder', models.CharField(max_length=100)),
                ('bank', models.CharField(max_length=100)),
                ('bank_code', models.CharField(max_length=100)),
                ('bank_account', models.CharField(max_length=100)),
                ('status', models.CharField(choices=[('waiting', '정산대기'), ('completed', '정산완료'), ('failed', '정산거부 (1:1문의 해주세요)')], default='waiting', max_length=20)),
                ('rejection_message', models.TextField(blank=True, null=True)),
                ('request_user_email', models.CharField(max_length=100)),
                ('request_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]