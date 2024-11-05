from django.urls import path
# Notification
from .views import GetNotificationDetail
from .views import DeleteNotification

# FCM token register
from .views import RegisterFCMToken

# FCM token data 
from .views import GetUserNotificationPreference

# FCM token preference change
from .views import ChangeNotificationPreference


# Flutter Start
urlpatterns = [
    # Notification
    path('api/get_notification/', GetNotificationDetail, name='notification-get-api-for-notification-page'),
    path('api/notification_delete/', DeleteNotification, name='delete_notification'),

    # FCM token register
    path('api/fcm_token_register/', RegisterFCMToken, name='register_fcm_token'),
    
    # FCM token preference (for notification page)
    path('api/get_user_notification_preference/', GetUserNotificationPreference, name='get_notification_preference_from_token_db'),

    path('api/change_user_notification_preference/', ChangeNotificationPreference, name='change_user_notification_preference')
]
