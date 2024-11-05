from django.urls import path

# Company Policy
from .views import GetCompanyPolicy

# Privacy Policy
from .views import GetPrivacyPolicy


urlpatterns = [
    path('api/get_company_policy/', GetCompanyPolicy, name='fetch-company-policy'),
    path('api/get_privacy_policy/', GetPrivacyPolicy, name='fetch-privacy-policy')
]
