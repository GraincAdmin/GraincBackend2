from django.contrib import admin
from . models import Community_Articles, CommunityBookmark, CommunityBookmarkFolder, CommunityBookmark, Community_Article_Comment, Community_Article_Comment_Reply
from .models import Community_Membership_Article_Free_Trial

# reporting
from .models import ReportedArticlesComments
# Register your models here.

class Community_Articles_Admin(admin.ModelAdmin):
    list_display = ['author', 'subject', 'category', 'sub_category','create_date']

admin.site.register(Community_Articles, Community_Articles_Admin)

admin.site.register(Community_Membership_Article_Free_Trial)
    

class Community_Article_Comment_Admin(admin.ModelAdmin):
    list_display = ['author', 'article', 'create_date']

admin.site.register(Community_Article_Comment, Community_Article_Comment_Admin)



class Community_Article_Comment_Reply_Admin(admin.ModelAdmin):
    list_display = ['author', 'reply_comment', 'create_date']

admin.site.register(Community_Article_Comment_Reply, Community_Article_Comment_Reply_Admin)




class Community_Bookmark_Folder_Admin(admin.ModelAdmin):
    list_display = ['folder_owner', 'folder_name']

admin.site.register(CommunityBookmarkFolder, Community_Bookmark_Folder_Admin)


class Community_Bookmark_Admin(admin.ModelAdmin):
    list_display = ['bookmark_folder', 'bookmark_article']

admin.site.register(CommunityBookmark, Community_Bookmark_Admin)


class Reported_Article_Admin(admin.ModelAdmin):
    list_display = ['type', 'reported_article']

admin.site.register(ReportedArticlesComments, Reported_Article_Admin)