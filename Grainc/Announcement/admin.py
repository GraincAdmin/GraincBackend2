from django.contrib import admin

# Register your models here.
from .models import Announcement

class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('subject', 'create_date')

admin.site.register(Announcement, AnnouncementAdmin)