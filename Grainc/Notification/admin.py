from django.contrib import admin

# Register your models here.
from .models import Notification

class NotificationAdmin(admin.ModelAdmin):
    list_display = ('notification_type', 'notification_create_user', 'create_date')
    search_fields = ('notification_type', 'notification_create_user__username')
    list_filter = ('notification_type', 'create_date')
    
    # Using filter_horizontal to make it easier to manage ManyToMany fields
    filter_horizontal = ('receivers', 'notification_on_read', 'notification_on_delete')

    # Using raw_id_fields for ForeignKey fields to improve performance with large datasets
    raw_id_fields = (
        'notification_create_user', 
        'notification_article', 
        'notification_comment',
        'notification_comment_reply',
        'notification_donation',
        'notification_donation_withdrawal',
        'notification_inquiry',
        'notification_announcement'
    )

    # Customizing the form to display ManyToMany fields nicely
    fieldsets = (
        (None, {
            'fields': ('create_date', 'notification_type', 'notification_create_user', 'receivers', 'notification_on_read', 'notification_on_delete')
        }),
        ('Related Models', {
            'fields': (
                'notification_article', 
                'notification_comment',
                'notification_comment_reply',
                'notification_donation',
                'notification_donation_withdrawal',
                'notification_inquiry',
                'notification_announcement'
            ),
            'classes': ('collapse',)
        }),
    )

# Registering the models and admin classes
admin.site.register(Notification, NotificationAdmin)

