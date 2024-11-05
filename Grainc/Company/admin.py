from django.contrib import admin
from .models import Company_Announcement
# Register your models here.
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ['Company_Announcement_Subject', 'Company_Announcement_Date']

admin.site.register(Company_Announcement, AnnouncementAdmin)