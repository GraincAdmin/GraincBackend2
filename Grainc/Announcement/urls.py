from django.urls import path

# Announcement Main
from .views import GetAnnouncement
# Announcement Detail 
from .views import GetAnnouncementDetail

# Importance Announcement
from .views import GetImportantAnnouncement

urlpatterns = [
    path('api/get_announcements/', GetAnnouncement, name='fetch-announcement-for-announcement-main'),
    path('api/get_announcement_detail/<int:announcement_id>/', GetAnnouncementDetail, name='fetch-announcement-detail'),
    path('api/get_importance_announcement/', GetImportantAnnouncement, name='get-importance-announcement')
]
