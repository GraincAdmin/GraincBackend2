from django.urls import path

#server status check 
from .views import ServerStatusCheck
# Login
from .views import AdminLogin

# Dashboard 
from .views import CustomAdminDashBoard

# User management
from .views import AdminUserInformationSimple
from .views import AdminUserInformationDetail
# Community Management
from .views import AdminCommunitySimple
from .views import AdminCommunityDetail
from .views import AdminCommunityDelete
# Violation Management
from .views import AdminViolationReportSimple
from .views import AdminViolationDetail
from .views import getReportedContent
# Donation Record 
from .views import AdminDonationRecordSimple
from .views import AdminDonationRecordDetail
# Donation Withdrawal Record
from .views import AdminDonationWithdrawalRecordSimple
from .views import AdminDonationWithdrawalRecordDetail
# Inquiry
from .views import AdminInquiryManagement
from .views import InquiryManagementDetail
# Company Announcement
from .views import AdminCompanyAnnouncementManagement
from .views import AdminAnnouncementDetail
from .views import AdminNewAnnouncement
# Company Policy
from .views import AdminCompanyPolicy
from .views import AdminPolicyDetail
from .views import AdminNewPolicy
from .views import AdminPolicyDelete
# Company Announcement
from .views import AdminLTDAnnouncement
from .views import AdminLTDAnnouncementDetail
from .views import AdminNewLTDAnnouncement
from .views import AdminLTDAnnouncementDelete
# Survey
from .views import AdminSurvey
from .views import AdminSurveyDetail
# PO performance
from .views import AdminGetRevenueData

# test

urlpatterns = [
    # Server Status Check
    path('api/server_check/', ServerStatusCheck, name='server_status_check'),

    # Login
    path('api/admin_login/', AdminLogin, name='admin_login'),

    path('api/custom_admin_dashboard_data/', CustomAdminDashBoard, name='admin_dashboard_all_data'),

    # user management
    path('api/custom_admin_user_management/', AdminUserInformationSimple, name='fetch_user_basic_information'),
    path('api/custom_admin_user_detail/<int:user_id>/', AdminUserInformationDetail, name='fetch-specific-user-detail'),

    # community management
    path('api/custom_admin_community_management/', AdminCommunitySimple, name='fetch_community_basic_information'),
    path('api/custom_admin_community_management_detail/<int:article_id>/', AdminCommunityDetail, name='fetch_community_article_detail'),
    path('api/custom_admin_article_delete/<int:article_id>/', AdminCommunityDelete, name='handle_community_article_delete'),

    # violation management
    path('api/custom_admin_violation_management/', AdminViolationReportSimple, name='fetch_community_article_comment_reply_reports'),
    path('api/custom_admin_violation_management_detail/<int:violation_id>/', AdminViolationDetail, name='fetch_community_article_comment_reply_reports_detail'),
    path('api/custom_admin_violation_content/<int:violation_id>/', getReportedContent, name='get_violation_content_for_check'),

    # donation record
    path('api/custom_admin_donation_record/', AdminDonationRecordSimple, name='fetch_donation_record'),
    path('api/custom_admin_donation_record_detail/<int:donation_id>/', AdminDonationRecordDetail, name='fetch_donation_record_detail'),

    # donation withdrawal record
    path('api/custom_admin_donation_withdrawal_record/', AdminDonationWithdrawalRecordSimple, name='fetch_donation_withdrawal_request'),
    path('api/custom_admin_donation_withdrawal_detail/<int:withdrawal_record_id>/', AdminDonationWithdrawalRecordDetail, name='fetch_donation_withdrawal_detail'),

    # Inquiry
    path('api/custom_admin_inquiry_management/', AdminInquiryManagement, name='fetch_inquiry_basic_information'),
    path('api/custom_admin_inquiry_management_detail/<int:inquiry_id>/', InquiryManagementDetail, name='fetch_inquiry_management_detail'),

    # Company Announcement
    path('api/custom_admin_company_announcement/', AdminCompanyAnnouncementManagement, name='fetch_company_announcement_management_information'),
    path('api/custom_admin_announcement_detail/<int:announcement_id>/', AdminAnnouncementDetail, name='fetch_announcement_detail'),
    path('api/custom_admin_new_announcement/', AdminNewAnnouncement, name='post-new-announcement'),

    # Company Policy
    path('api/custom_admin_company_policy/', AdminCompanyPolicy, name='fetch_company_policy_basic'),
    path('api/custom_admin_policy_detail/<str:policy_type>/<int:policy_id>/', AdminPolicyDetail, name='fetch_policy_detail'),
    path('api/custom_admin_new_policy/<str:policy_type>/', AdminNewPolicy, name='post_new_policy'),
    path('api/custom_admin_delete_policy/<str:policy_type>/<int:policy_id>/', AdminPolicyDelete, name='delete policy'),

    # Company Announcement LTD

    path('api/custom_admin_company_LTD_announcement/', AdminLTDAnnouncement, name='LTD_legal_announcement'),
    path('api/custom_admin_company_LTD_announcement_detail/<int:announcement_id>/', AdminLTDAnnouncementDetail, name='fetch_announcement_detail'),
    path('api/custom_admin_new_company_LTD_announcement/', AdminNewLTDAnnouncement, name='post-new-company-LTD-announcement'),
    path('api/custom_admin_company_LTD_announcement_delete/<int:announcement_id>/', AdminLTDAnnouncementDelete, name='delete_announcement_ltd'),

    # Survey
    path('api/custom_admin_survey/', AdminSurvey, name='get_survey'),
    path('api/custom_admin_survey_detail/<int:survey_id>/', AdminSurveyDetail, name='get_survey_detail'),

    # PO performance
    path('api/custom_admin_get_company_revenue/', AdminGetRevenueData, name='get_company_revenue')
]
