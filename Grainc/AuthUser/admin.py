from django.contrib import admin
from .models import ServiceUser, UserFCMToken

# Inline for subscribers
class SubscribersInline(admin.TabularInline):
    model = ServiceUser.subscribers.through
    extra = 1




admin.site.register(ServiceUser)


admin.site.register(UserFCMToken)
