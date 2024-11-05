# urls.py
from django.urls import path
from . import views

# Company Announcements
from .views import GetCompanyAnnouncements
# Company Announcements Detail
from .views import GetAnnouncementDetail
urlpatterns = [
    path('api/get_company_announcements/', GetCompanyAnnouncements, name='fetch-company-announcements'),
    path('api/company_announcement_detail/<int:announcement_id>/', GetAnnouncementDetail, name='fetch-announcement-detail')
]
