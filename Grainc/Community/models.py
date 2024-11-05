# Create your models here.
from django.db import models
from django.conf import settings 
from django.utils import timezone
import django.utils



# Create your models here.
class Community_Articles(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    create_date = models.DateTimeField(default=django.utils.timezone.now)
    subject = models.CharField(max_length=100)
    category = models.CharField(max_length=50, blank=True, null=True)
    sub_category = models.CharField(max_length=50, blank=True, null=True)
    hashtags = models.JSONField(blank=True, null=True)
    main_content = models.TextField()
    views = models.PositiveIntegerField(default=0)
    views_validation = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="views_validation", blank=True)
    likes = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='likes', blank=True)
    comments = models.PositiveBigIntegerField(default=0)
    images = models.BooleanField()
    saved_article = models.BooleanField(default=False)

    is_hidden_admin = models.BooleanField(default=False)

    # Membership content
    is_membership = models.BooleanField(default=False, null=True)

    # S3
    unique_folder_name = models.CharField(max_length=100, blank=True, null=True)
    def __str__(self):
        return self.subject
    
class Community_Membership_Article_Free_Trial(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    article = models.ForeignKey(Community_Articles, on_delete=models.CASCADE)
    view_date = models.DateField(default=timezone.now)

    class Meta:
        unique_together = ('user', 'article', 'view_date')

    def __str__(self):
        return f'{self.user.username} viewed {self.article.subject} on {self.view_date}'

class Community_Article_Comment(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='comment_author')
    article = models.ForeignKey(Community_Articles, on_delete=models.CASCADE)
    create_date = models.DateTimeField(default=django.utils.timezone.now)
    comment = models.TextField()
    comment_likes = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='comment_likes', blank=True)
    reply_count = models.PositiveBigIntegerField(default=0)

    def __str__(self):
        return f"{self.article.subject} "


class Community_Article_Comment_Reply(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    reply_comment = models.ForeignKey(Community_Article_Comment, on_delete=models.CASCADE)
    create_date = models.DateTimeField(default=django.utils.timezone.now)
    reply = models.TextField()
    def __str__(self):
        return f"{self.reply_comment.id} "
    


#Community_Bookmark
class CommunityBookmarkFolder(models.Model):
    folder_name = models.CharField(max_length=20)
    create_date = models.DateTimeField(default=django.utils.timezone.now)
    folder_owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)
    bookmarks = models.ManyToManyField(Community_Articles, blank=True)

    def __str__(self):
        return f"{self.folder_name, self.folder_owner.username} "

class CommunityBookmark(models.Model):
    bookmark_folder = models.ForeignKey(CommunityBookmarkFolder, on_delete=models.CASCADE)
    bookmark_article = models.ForeignKey(Community_Articles, on_delete=models.CASCADE)
    order_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order_added']



#article reporting

class ReportedArticlesComments(models.Model):
    reported_article = models.ForeignKey(Community_Articles, on_delete=models.SET_NULL, blank=True, null=True)
    reported_comment = models.ForeignKey(Community_Article_Comment, on_delete=models.SET_NULL, blank=True, null=True)
    create_date = models.DateTimeField(default=django.utils.timezone.now)
    reported_comment_reply = models.ForeignKey(Community_Article_Comment_Reply, on_delete=models.SET_NULL, blank=True, null=True)
    reported_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True)
    type = models.CharField(max_length=100)
    detail = models.TextField(blank=True, null=True)
    
    is_task_done = models.BooleanField(default=False)

