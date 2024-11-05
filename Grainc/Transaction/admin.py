from django.contrib import admin
from .models import Membership_Article_Donation_Record
from .models import Membership_Donation_Withdrawal_Request
# Register your models here.


class Donation_Record_Admin(admin.ModelAdmin):
    list_display = ['donator', 'amount', 'donation_date', 'article']

admin.site.register(Membership_Article_Donation_Record, Donation_Record_Admin)


class Donation_Withdrawal_Record_Admin(admin.ModelAdmin):
    list_display = ['request_date', 'amount', 'account_holder', 'request_user']


admin.site.register(Membership_Donation_Withdrawal_Request, Donation_Withdrawal_Record_Admin)