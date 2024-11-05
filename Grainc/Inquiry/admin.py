from django.contrib import admin
from .models import Inquiry
# Register your models here.

class InquiryAdmin(admin.ModelAdmin):
    list_display = ['User', 'Inquiry_subject', 'Inquiry_type', 'Inquiry_date', 'is_replied']

admin.site.register(Inquiry, InquiryAdmin)