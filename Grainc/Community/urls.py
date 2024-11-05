# urls.py
from django.urls import path
from . import views

#home

#community home
from .views import HomeCommunityArticleMostLiked, HomeCommunityArticleLatest

#community main
from .views import MainCommunityArticle
# Community Main Flutter start api

#article_detail
from .views import get_community_article, AuthorsArticle, ArticleRecommendation, community_article_view_update
from .views import articleFreeTrial

#bookmark check
from .views import BookmarkFolder, BookmarkStatusCheck

#bookmark system
from . views import CommunityBookmarkAdd, CommunityBookmarkFolderAdd, CommunityBookmarkFolderNameEdit
#bookmark page
from .views import GetBookmarkedArticles, DeleteCommunityBookmarkFolder

#Community Like
from .views import CommunityLike, CommunityLikeStatus

# Membership Donation
from .views import MembershipDonation

#Community Comment System
from .views import CommunityCommentUpload, CommunityArticleComments, CommunityCommentReply, CommunityCommentReplyView
from .views import CommunityCommentDelete, CommunityCommentReplyDelete
from .views import GetCommunityCommentPageDetail
from .views import CommunityCommentLike, CommunityCommentLikeCount
from .views import CommunityCommentModification

#Article Upload
from .views import article_upload

#Article Modification
from .views import GetModifyingArticleData

#Saved Article
from .views import GetUserSavedArticle, LoadUserSavedArticle, DeleteUserSavedArticle

#User Profile
from .views import GetUserProfileArticle

#Search
from .views import GetSearchedArticle

# Article Reporting
from .views import CreateArticleReport


urlpatterns = [

    # Community Home and Main
    path('api/article_home_latest/', HomeCommunityArticleLatest, name='home_article_create_date_order'),
    path('api/article_home_most_like/', HomeCommunityArticleMostLiked, name='home_article_like_order'),

    # Community Detail
    path('api/community_article/<int:article_id>/', get_community_article, name='community-article-detail'),
    path('api/main_community_article/', MainCommunityArticle, name="community-section-main-article-api"),
    path('api/handle_article_free_trial/', articleFreeTrial, name='free trial + adding free trial'),
    # Community Main Flutter start api

    path('api/article_views_update/<int:article_id>/', community_article_view_update, name='update_article_views'),
    path('api/authors_article/<int:current_article_id>/', AuthorsArticle, name='community-article-main-authors-articles'),
    path('api/article_recommendation/<int:current_article_id>/', ArticleRecommendation, name="article-main-recommendation"),

    #bookmark Basic
    #bookmark Flutter Mobile Start Api
    path('api/user_bookmark_folder/', BookmarkFolder, name='get_user_community_bookmark'),
    path('api/community_bookmark_status/<int:user_id>/<int:article_id>/', BookmarkStatusCheck, name='bookmark_status_check'),

    #bookmark system
    path('api/bookmark_folder_add/', CommunityBookmarkFolderAdd, name='bookmark_folder_add'),
    path('api/bookmark_add_delete/<int:article_id>/<int:folder_id>/<int:user_id>/', CommunityBookmarkAdd, name='bookmark_add_delete_system_community'),
    #bookmark page
    path('api/bookmark_page_article/', GetBookmarkedArticles, name='fetch-bookmarked-article-for-bookmark-page'),
    path('api/bookmark_folder_delete/', DeleteCommunityBookmarkFolder, name='post-to-delete-community-bookmark-folder'),
    path('api/bookmark_folder_name_change/', CommunityBookmarkFolderNameEdit, name='bookmark-folder-name-change'),

    #like system
    path('api/article_like_status/<int:user_id>/<int:article_id>/', CommunityLikeStatus, name="user_community_like_check"),
    path('api/article_like/<int:user_id>/<int:article_id>/', CommunityLike, name='user_community_article_like'),

    # Membership Donation
    path('api/article_membership_donation/', MembershipDonation, name='handle_membership_donation'),

    #Comment
    path('api/article_comments_main/<int:article_id>/<str:page_section>/', CommunityArticleComments, name='community-article-comment-main'),
    path('api/article_comment_upload/<int:article_id>/', CommunityCommentUpload, name='community-comment-upload'),
    path('api/article_comment_page_detail/<int:article_id>/', GetCommunityCommentPageDetail, name='get-article-detail-for-comment-page'),
    path('api/article_comment_delete/', CommunityCommentDelete, name='delete-community-comment-delete'),
    path('api/article_comment_like/<int:comment_id>/', CommunityCommentLike, name='comment-comment-like-dislike'),
    path('api/article_comment_like_count/<int:comment_id>/', CommunityCommentLikeCount, name='community-comment-count'),
    # api start from flutter (comment)
    path('api/article_comment_modification/', CommunityCommentModification, name='comment-modification'),
    #Comment Reply
    path('api/article_comment_reply_view/<int:comment_id>/', CommunityCommentReplyView, name='get-comment-reply'),
    path('api/article_comment_reply/<int:comment_id>/', CommunityCommentReply, name='comment_reply_post_form'),
    path('api/article_comment_reply_delete/', CommunityCommentReplyDelete, name='community_comment_reply_delete'),

    #Article_Upload
    path('api/article_upload/', article_upload, name='community-article-upload'),

    # Article Modification
    path('api/get_article_modification_data/<int:article_id>/', GetModifyingArticleData, name='community-article-modification'),

    # Saved Article
    path('api/get_user_saved_article/', GetUserSavedArticle, name='get-user-saved-articles'),
    path('api/load_user_saved_article/<int:article_id>/', LoadUserSavedArticle, name='load-user-saved-article'),
    path('api/delete_user_saved_article/<int:article_id>/', DeleteUserSavedArticle, name='delete-user-saved-article'),

    #User Profile Flutter Migrated
    path('api/get_user_article/<int:user_id>/', GetUserProfileArticle, name='fetch-article-for-userprofile'),

    #Searched Result
    path('api/article_search/', GetSearchedArticle, name='fetch-searched-article'),

    # Article Reporting
    path('api/report_article/', CreateArticleReport, name='report_article'),
]