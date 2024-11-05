from django import forms
from .models import CommunityBookmarkFolder, CommunityBookmark, Community_Article_Comment, Community_Article_Comment_Reply, Community_Articles, CommunityBookmarkFolder
from .models import Community_Membership_Article_Free_Trial

# Reporting
from .models import ReportedArticlesComments

class CommunityBookmarkFolderForm(forms.ModelForm):
    class Meta:
        model = CommunityBookmarkFolder
        fields = ('folder_name', 'folder_owner')

class CommunityBookmarkForm(forms.ModelForm):
    class Meta:
        model = CommunityBookmark
        fields = ('bookmark_folder', 'bookmark_article')



class CommunityCommentForm(forms.ModelForm):
    class Meta:
        model = Community_Article_Comment
        fields = ('author', 'article', 'comment')

class CommunityCommentReplyForm(forms.ModelForm):

    class Meta:
        model = Community_Article_Comment_Reply
        fields = ['author', 'reply_comment', 'reply']


class CommunityArticleForm(forms.ModelForm):
    class Meta:
        model = Community_Articles
        fields = [
            'author', 
            'subject', 
            'category',
            'hashtags', 
            'sub_category', 
            'is_membership',
            'main_content', 
            'images', 
            'saved_article', 
            'unique_folder_name'
        ]


class ReportedArticlesCommentsForm(forms.ModelForm):
    class Meta:
        model = ReportedArticlesComments
        fields = [
            'reported_article', 
            'reported_comment',
            'reported_comment_reply',
            'type', 
            'detail'
        ]

