from rest_framework.decorators import api_view
from rest_framework.response import Response

# Company Policy
from .models import CompanyPolicy
from .serializer import CompanyPolicySerializer, CompanyPolicySelectorSerializer

# Privacy Policy
from .models import PrivacyPolicy
from .serializer import PrivacyPolicySerializer, PrivacyPolicySelectorSerializer

@api_view(['GET'])
def GetCompanyPolicy(request):
    history_company_policies = CompanyPolicy.objects.order_by('-create_date').all()
    selected_company_policy_id = request.GET.get('policy_id')

    try:
        company_policy = CompanyPolicy.objects.get(id=selected_company_policy_id)
    except:
        company_policy = history_company_policies.first()

    policy_serializer = CompanyPolicySerializer(company_policy)
    policy_selector_serializer = CompanyPolicySelectorSerializer(history_company_policies, many=True)
    return Response({
        'policy': policy_serializer.data,
        'policy_selector': policy_selector_serializer.data
    })


@api_view(['GET'])
def GetPrivacyPolicy(request):
    history_company_policies = PrivacyPolicy.objects.order_by('-create_date').all()
    selected_company_policy_id = request.GET.get('policy_id')

    try:
        company_policy = PrivacyPolicy.objects.get(id=selected_company_policy_id)
    except:
        company_policy = history_company_policies.first()

    policy_serializer = PrivacyPolicySerializer(company_policy)
    policy_selector_serializer = PrivacyPolicySelectorSerializer(history_company_policies, many=True)
    return Response({
        'policy': policy_serializer.data,
        'policy_selector': policy_selector_serializer.data
    })
