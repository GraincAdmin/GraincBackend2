from django.urls import path
#Donation Record
from .views import GetDonationAmount
from .views import GetUserDonationRecord
from .views import HandleDonationWithdrawalRequest
# Withdrawal Record
from .views import GetDonationWithdrawalHistory
from .views import GetDonationWithdrawalHistoryDetail
urlpatterns = [
    #Donation Record
    path('api/get_user_donation_amount/', GetDonationAmount, name='get_user_donation_amount'),
    path('api/get_user_donation_record/', GetUserDonationRecord, name='get_user_donation_record'),
    path('api/handle_donation_withdrawal/', HandleDonationWithdrawalRequest, name='handle_donation_withdrawal_request'),

    #Donation Withdrawal Record
    path('api/get_user_donation_withdrawal_record/', GetDonationWithdrawalHistory, name='donation_withdrawal_simple'),
    path('api/get_user_donation_withdrawal_record_detail/<int:record_id>/', GetDonationWithdrawalHistoryDetail, name='donation_withdrawal_detail')
]

