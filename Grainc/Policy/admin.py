from django.contrib import admin

# Register your models here.
from .models import CompanyPolicy, PrivacyPolicy

admin.site.register(CompanyPolicy)
admin.site.register(PrivacyPolicy)