from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView
from . import views

#login signup
from .views import MyTokenObtainPairView
from .views import CustomTokenRefreshView
from .views import SellReportAccountCreation

# social login
from .views import google_login, google_callback, google_callback_mobile
from .views import naver_login, naver_callback, naver_callback_mobile
from .views import kakao_login, kakao_callback, kakao_callback_mobile
from .views import SocialLoginUsernameRegistration

#signup data check
from .views import SignupEmailCheck
from .views import UsernameErrorCheck

#password reset
from .views import PasswordResetRequest
from .views import password_reset_authentication

#subscribe status
from .views import CheckUserSubscriberCommunity
from .views import ProfileSubscribeStatusCheck

#subscribe feature
from .views import HandelSubscribingFeatureCommunity
from .views import HandelSubscribingFeatureProfile

# User Subscribing Contents
from .views import getUserSubscribingContents
from .views import getUserSubscribingUsers

# Global User State Management
from .views import GetUserProfileImage

# User Profile
from .views import GetUserProfileInformation
from .views import MyPageGetUserProfileInformation

#MyPage

# My Profile
from .views import PostNewProfileImage
from .views import ModifyUserProfile
from .views import GetMyPageProfileData
from .views import MyPagePasswordChange
from .views import getUserProfileArticle


#CommunityManagement
from .views import GetUserCommunityArticle
from .views import DeleteUserCommunityArticle

# Account Cancel 
from .views import handleCancelAccount


app_name = 'AuthUser'


urlpatterns = [

    # Auth Control
    path('api/login_token/', MyTokenObtainPairView.as_view(), name='login_token'),
    path('api/token/refresh/', CustomTokenRefreshView.as_view(), name='refresh-user-token'),#토큰 재발급하기
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),

    # Social Login
    path('api/google_login/', google_login, name='google_login'),
    path('api/login/google/callback/', google_callback, name='google_callback'),
    path('api/login/google_callback_mobile/', google_callback_mobile, name='google_callback_mobile'),

    path('api/naver_login/', naver_login, name='naver_login'),
    path('api/login/naver/callback/', naver_callback, name='naver_callback'),
    path('api/login/naver/callback_mobile/', naver_callback_mobile, name='naver_callback_naver'),

    path('api/kakao_login/', kakao_login, name='kakao_login'),
    path('api/login/kakao/callback/', kakao_callback, name='kakao_callback'),
    path('api/login/kakao/callback_mobile/', kakao_callback_mobile, name='kakao_callback_mobile'),
    
    path('api/username_register/', SocialLoginUsernameRegistration, name='username_register'),

    
    #signup_api
    path('api/signup/', SellReportAccountCreation, name='sellreports-user-creation-post-handel'),
    #signup data validity check
    path('api/signup_email_check/', SignupEmailCheck, name='signup-email-check'),
    path('api/signup_username_check/', UsernameErrorCheck, name='signup-username-check'),
    path('api/signup_email_authentication/', views.signup_email_authentication, name='signup_email_authentication'),
    # password reset
    path('api/password_reset_request/', PasswordResetRequest, name='password_reset'),
    path('api/password_reset_authentication/', password_reset_authentication, name='password_reset_authenticated'),

    #Community Subscribe status (deprecated)
    path('api/subscribe_status_community/<int:article_id>/<int:user_id>/', CheckUserSubscriberCommunity, name='community-article-subscription-check'),
    #Community Subscribe feature
    path('api/handel_subscribe_community/', HandelSubscribingFeatureCommunity, name='handel-subscribe-unsubscribe-community'),


    #Profile Subscribe status (deprecated)
    path('api/subscribe_status_profile/<int:authUser_id>/<int:user_id>/', ProfileSubscribeStatusCheck, name='profile-subscription-check'),
    #Profile Subscribe Feature
    path('api/handel_subscribe_profile/', HandelSubscribingFeatureProfile, name='handel-subscribe-unsubscribe-profile'),

    # Global User State Management
    path('api/get_user_profile_image/<int:user_id>/', GetUserProfileImage, name='get-user-profile-image-for-AuthContext'),

    # Subscribing Contents
    path('api/get_user_subscribing_contents/', getUserSubscribingContents, name='get-user-subscribing-user-contents'),
    path('api/get_user_subscribing_users/', getUserSubscribingUsers, name='get-user-subscribing-users'),


    #User Profile
    path('api/get_user_profile/<int:user_id>/', GetUserProfileInformation, name='fetch-user-information-for-profile'),


    #MyPage

    #My Profile
    path('api/post_new_profile/', PostNewProfileImage, name='post-new-profile-image'),
    path('api/post_updated_profile/', ModifyUserProfile, name='post-new-user-introduction'),
    path('api/my_page_profile_data/', GetMyPageProfileData, name='fetch-user-my-page-profile-data'),
    path('api/password_change/', MyPagePasswordChange, name='my-page-password-change'),

    # flutter start
    path('api/my_page_get_user_profile/<int:user_id>/', MyPageGetUserProfileInformation, name='fetch-user-information-for-profile'),

    # My Profile Flutter start api
    path('api/my_profile_article/', getUserProfileArticle, name='my-profile-article'),

    #CommunityManagement
    path('api/get_user_article_my_page/<int:user_id>/', GetUserCommunityArticle, name='fetch-user-article-for-my-page'),
    path('api/delete_article/', DeleteUserCommunityArticle, name='delete-community-article'),

    #Account Cancel 
    path('api/request_account_cancel/', handleCancelAccount, name='account_cancel_request')

]
