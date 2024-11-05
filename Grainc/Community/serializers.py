from .models import Community_Articles
from rest_framework import serializers
from django.utils.html import strip_tags
from django.utils.safestring import mark_safe
from django.contrib.humanize.templatetags.humanize import intcomma

# auth
from AuthUser.models import ServiceUser

# global function
from Grainc.Global_Function.ContentDataFormatter import create_date_formatter
from Grainc.Global_Function.AuthControl import decodeUserToken
from Grainc.Global_Function.ImgProcessorQuill import extract_img_urls

#Bookmark
from .models import CommunityBookmarkFolder

#Comments
from .models import Community_Article_Comment, Community_Article_Comment_Reply


def BookmarkStatusCheckSerializer(user, article_id):
    try:
        selected_article = Community_Articles.objects.get(id=article_id)
    except ServiceUser.DoesNotExist:
        return
    except Community_Articles.DoesNotExist:
        return 
    
    user_bookmark_folder_exists = CommunityBookmarkFolder.objects.filter(folder_owner=user, bookmarks=selected_article).exists()
    
    return user_bookmark_folder_exists

class CommunityArticleSerializers(serializers.ModelSerializer):
    class Meta:
        model = Community_Articles    
        fields = (
            'id', 'author', 'create_date', 'subject', 
            'main_content', 'views', 'views_validation', 
            'category', 'sub_category', 'likes', 'comments', 'images', 'is_membership'
        )  

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['create_date'] = create_date_formatter(instance.create_date)
        if instance.author:
            data['author_id'] = instance.author.id
            data['author_username'] = instance.author.username
            if instance.author.profile_image:
                data['author_profile_image'] = instance.author.profile_image.url
        
        is_main_content = self.context.get('is_main_content', False)
        if is_main_content:
            data['main_content'] = mark_safe(instance.main_content)
        elif not is_main_content:
            data['description'] = strip_tags(instance.main_content)
            data['community_image'] = extract_img_urls(instance.main_content)
            
        data['likes_count'] = intcomma(instance.likes.count())
        data['views_count'] = intcomma(instance.views)
        data['comments_count'] = intcomma(instance.comments)

        # user information for community main
        is_user_data = self.context.get('is_user_data', False)  # Initialize with False if not present

        if is_user_data:
            if instance.author:
                data['author_introduction'] = intcomma(instance.author.introduction)
                data['author_subscriber_count'] = intcomma(instance.author.subscribers.count())
                data['author_article_count'] = intcomma(Community_Articles.objects.filter(author=instance.author).count())

        user = self.context.get('user')
        data['is_bookmarked'] = False
        if user:
            data['is_bookmarked'] = BookmarkStatusCheckSerializer(user, instance.id)
            
        return data



class CommunityArticleSerializersSimple(serializers.ModelSerializer):
    class Meta:
        model = Community_Articles
        fields = ('subject', 'category', 'main_content')
    

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['id'] = instance.id
        data['community_image'] = extract_img_urls(instance.main_content)
        return data
    
class CommunityBookmarkFolderSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommunityBookmarkFolder
        fields = ('folder_name', 'bookmarks')

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['id'] = instance.id

        # Query Optimization

        bookmarks = instance.bookmarks.all()

        data['bookmark_count'] = intcomma(bookmarks.count())

        folder_image_article = next((bm for bm in bookmarks if bm.images), None)

        if folder_image_article:
            data['folder_image'] = extract_img_urls(folder_image_article.main_content)

        return data
    

#Community Comments
class CommunityCommentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Community_Article_Comment
        fields = ('id' ,'author', 'create_date', 'comment', 'reply_count', 'comment_likes')

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['formatted_date'] = create_date_formatter(instance.create_date)
        if instance.author:
            data['author_id'] = instance.author.id
            data['author_username'] = instance.author.username
            if instance.author.profile_image:
                data['author_profile_image'] = instance.author.profile_image.url
        return data
    
class CommunityCommentReplySerializer(serializers.ModelSerializer):
    class Meta:
        model = Community_Article_Comment_Reply
        fields = ('id' ,'author', 'create_date', 'reply')

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if instance.author:
            data['author_id'] = instance.author.id
            data['author_username'] = instance.author.username
            if instance.author.profile_image:
                data['author_profile_image'] = instance.author.profile_image.url
        data['formatted_date'] = create_date_formatter(instance.create_date)
        return data
    


class MyPageCommunityArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Community_Articles
        fields = ('id' ,'subject', 'create_date', 'category', 'views', 'comments', 'main_content')
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['article_create_date'] = create_date_formatter(instance.create_date)
        data['article_id'] = instance.id
        data['community_image'] = extract_img_urls(instance.main_content)
        return data
    
"""
flutter api started spread to web
this includes detection of page change within the myPage user profile article 
1. my normal community article
2. my membership community article
3. donated article
4. liked article (normal + membership included)
"""

class MyProfileCommunityArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Community_Articles
        fields = ('id' ,'subject', 'main_content','create_date', 'category', 'sub_category','views', 'comments', 'is_membership')
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['article_create_date'] = create_date_formatter(instance.create_date)
        data['article_id'] = instance.id
        data['formatted_views_count'] = intcomma(instance.views)
        data['formatted_comments_count'] = intcomma(instance.comments)
        data['community_image'] = extract_img_urls(instance.main_content)
        is_device_pc = self.context.get('is_device_pc', False)  # Initialize with False if not present
        if is_device_pc:
            data['description'] = strip_tags(instance.main_content)
        else:
            data.pop('main_content', None)
        return data

# Community Article Modification and Saved Article

class UploadedArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Community_Articles
        fields = ('id', 'subject', 'category', 'sub_category', 'main_content')

class UserSavedArticleStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Community_Articles
        fields = ('id' ,'subject', 'create_date')

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['formatted_date'] = create_date_formatter(instance.create_date)
        return data
    

