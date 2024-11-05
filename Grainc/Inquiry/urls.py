from django.urls import path

# Inquiry
from .views import GetInquiryHistory

# Inquiry 
from .views import GetInquiryReply

# New Inquiry
from .views import postNewInquiry

urlpatterns = [
    path('api/get_user_inquiry/', GetInquiryHistory, name='fetch-user-inquiry-history'),
    path('api/get_inquiry_reply/<int:inquiry_id>/', GetInquiryReply, name='fetch-user-inquired-data'),
    path('api/new_inquiry/', postNewInquiry, name='post-new-inquiry')
]
