# Generated by Django 5.1.3 on 2024-11-05 09:25

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CompanyCarryingCapacity',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('new_customers', models.PositiveIntegerField(default=0)),
                ('percentage_loss', models.PositiveIntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='CompanyRetention',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('retention', models.FloatField(default=0)),
                ('retention_period', models.CharField(choices=[('daily', 'Daily'), ('weekly', 'Weekly'), ('monthly', 'Monthly')], default='monthly', max_length=10)),
            ],
        ),
        migrations.CreateModel(
            name='CompanyRevenueStatistics',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('defined_revenue', models.PositiveIntegerField(default=0)),
                ('combined_revenue_data', models.JSONField(blank=True, null=True)),
            ],
        ),
    ]