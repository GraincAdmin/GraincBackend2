from celery import shared_task
from django.utils import timezone
from .models import Notification
from AuthUser.models import UserFCMToken, ServiceUser

from Notification.forms import NotificationForm
from Grainc.Global_Function.FirebaseNotification import SendFCMNotification 

@shared_task
def delete_old_notifications():
    # Calculate the date 7 days ago
    seven_days_ago = timezone.now() - timezone.timedelta(days=7)
    
    # Delete notifications older than 7 days
    old_notifications = Notification.objects.filter(create_date__lt=seven_days_ago)
    old_notifications.delete()


# FCM Notification Functions

@shared_task
def CreateNewNotification(type, content):

    notification_author = None
    receivers = None
    foreign_key_type = None

    notification_subject = None
    notification_content = None
    notification_url = None

    notification_types = {
        'article': {
            'author': lambda c: c.author,
            'receivers': lambda c: c.author.subscribers,
            'fk_type': 'notification_article',

            'title': lambda c: c.author,
            'content': lambda c: c.subject,
            'url': '/article_detail'
        },
        'comment': {
            'author': lambda c: c.author,
            'receivers': lambda c: c.article.author,
            'fk_type': 'notification_comment',

            'title': lambda c: c.subject,
            'content': lambda c: f'{c.author}님 이 댓글을 작성했습니다',
            'url': '/article_detail'
        },
        'comment_reply': {
            'author': lambda c: c.author,
            'receivers': lambda c: c.reply_comment.author,
            'fk_type': 'notification_comment_reply',

            'title': lambda c: c.reply_comment.article.subject,
            'content': lambda c: f'{c.author}님 이 답글을 작성했습니다',
            'url': '/article_detail'
        },
        'donation': {
            'author': lambda c: c.donator,
            'receivers': lambda c: c.article.author,
            'fk_type': 'notification_donation',

            'title': '후원알림',
            'content': lambda c: f'{c.donator.username}님 이 {c.subject}글에 후원했습니다',
            'url': '/article_detail'
        },
        'donation_withdrawal': {
            'author': ServiceUser.objects.filter(is_admin=True, id=1),
            'receivers': lambda c: c.User,
            'fk_type': 'notification_donation_withdrawal',

            'title': '후원금 알림',
            'content': '',
            'url': '/article_detail'
        },
        'inquiry': {
            'author': ServiceUser.objects.filter(is_admin=True, id=1),
            'receivers': lambda c: c.User,
            'fk_type': 'notification_inquiry',

            'title': '문의알림',
            'content': '문의 답변이 도착했습니다',
            'url': '/article_detail'
        },
        'announcement': {
            'author': ServiceUser.objects.filter(is_admin=True, id=1),
            'receivers': ServiceUser.objects.all(),
            'fk_type': 'notification_announcement',

            'title': '공지사항',
            'content': lambda c: c.Inquiry_subject,
            'url': '/article_detail'
        }
    }

    if type in notification_types:
        notification_author = notification_types[type]['author'](content)
        receivers = notification_types[type]['receivers'](content)
        foreign_key_type = notification_types[type]['fk_type']
        notification_subject = notification_types[type]['title']
        notification_content = notification_types[type]['content']
        notification_url = notification_types[type]['url']

        if notification_author and receivers:
            
            try:
                if type in ['comment', 'comment_reply'] and notification_author == receivers:
                    return  # Don't send a notification if the author is the receiver

                new_notification_data = {
                    'notification_type': type,
                    'notification_create_user': notification_author,
                    'receivers': [receivers],
                    foreign_key_type: content
                }
                
                notification_form = NotificationForm(new_notification_data)

                if notification_form.is_valid():
                    notification_form.save()

                    receivers_fcm_tokens = UserFCMToken.objects.filter(user=receivers)
                    if receivers_fcm_tokens.exists():
                        for fcm_tokens in receivers_fcm_tokens:

                            SendFCMNotification(
                                fcm_tokens.fcm_token, 
                                notification_subject,
                                notification_content,
                                notification_url
                            )
            except:
                pass


