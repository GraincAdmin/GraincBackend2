# Generated by Django 5.1.3 on 2024-11-05 09:25

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('Announcement', '0001_initial'),
        ('Community', '0001_initial'),
        ('Inquiry', '0001_initial'),
        ('Transaction', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('notification_type', models.CharField(choices=[('article', 'Article'), ('comment', 'Comment'), ('comment_reply', 'CommentReply'), ('donation', 'Donation'), ('donation_withdrawal', 'DonationWithdrawal'), ('inquiry', 'Inquiry'), ('announcement', 'Announcement')], max_length=20)),
                ('is_sent', models.BooleanField(default=False)),
                ('notification_announcement', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='Announcement.announcement')),
                ('notification_article', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='Community.community_articles')),
                ('notification_comment', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='Community.community_article_comment')),
                ('notification_comment_reply', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='Community.community_article_comment_reply')),
                ('notification_create_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notifications_created', to=settings.AUTH_USER_MODEL)),
                ('notification_donation', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='Transaction.membership_article_donation_record')),
                ('notification_donation_withdrawal', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='Transaction.membership_donation_withdrawal_request')),
                ('notification_inquiry', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='Inquiry.inquiry')),
                ('notification_on_delete', models.ManyToManyField(related_name='notification_deleted_user', to=settings.AUTH_USER_MODEL)),
                ('notification_on_read', models.ManyToManyField(related_name='received_notification', to=settings.AUTH_USER_MODEL)),
                ('receivers', models.ManyToManyField(blank=True, related_name='notifications_received', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
