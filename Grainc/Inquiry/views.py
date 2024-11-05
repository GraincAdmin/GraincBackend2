from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import jwt

# Rest
from rest_framework.decorators import api_view
from rest_framework.response import Response

# User Model
from AuthUser.models import ServiceUser

# Inquiry Model
from .models import Inquiry

# Inquiry Serializer
from .serializers import InquirySerializer

# Inquiry Form
from .forms import InquiryForm

# Global Function
from Grainc.Global_Function.AuthControl import decodeUserToken

# Create your views here.

@api_view(['GET'])
def GetInquiryHistory(request):
    auth_header = request.headers.get('Authorization')

    try: 
        user_id = decodeUserToken(auth_header)
        user = ServiceUser.objects.get(id=user_id)
        
        inquiry = Inquiry.objects.filter(
            User=user
        ).select_related(
            'User'
        ).order_by(
            '-Inquiry_date'
        )

        page = request.GET.get('page')
        paginator = Paginator(inquiry, 10)

        try:
            user_inquiry = paginator.page(page)
        except PageNotAnInteger:
            user_inquiry = paginator.page(1)
        except EmptyPage:
            user_inquiry = paginator.page(paginator.num_pages)

        serializer = InquirySerializer(user_inquiry, many=True)

        return Response({
            'inquiry': serializer.data,
            'max_page': paginator.num_pages,
            'current_page': page
        })

    except jwt.ExpiredSignatureError:
        return Response({'status': 'Token expired'}, status=401)
    except jwt.InvalidTokenError:
        return Response({'status': 'Invalid token'}, status=401)


@api_view(['GET'])
def GetInquiryReply(request, inquiry_id):
    auth_header = request.headers.get('Authorization')

    try:
        user_id = decodeUserToken(auth_header)
        user = ServiceUser.objects.get(id=user_id)
        
        inquiry = Inquiry.objects.get(id=inquiry_id)

        if (inquiry.User == user):
            serializer = InquirySerializer(inquiry)
            return Response(serializer.data)
        else:
            return Response({'status': 'Not Authorized for this user'}, status=403)

    except jwt.ExpiredSignatureError:
        return Response({'status': 'Token expired'}, status=401)
    except jwt.InvalidTokenError:
        return Response({'status': 'Invalid token'}, status=401)


@api_view(['POST'])
def postNewInquiry(request):
    auth_header = request.headers.get('Authorization')
    try:
        user_id = decodeUserToken(auth_header)
        user = ServiceUser.objects.get(id=user_id)

    except jwt.ExpiredSignatureError:
        return Response({'status': 'Token expired'}, status=401)
    except jwt.InvalidTokenError:
        return Response({'status': 'Invalid token'}, status=401)
    
    if request.method == 'POST':


        inquiry_data = {
            'User': user,
            'Inquiry_type': request.data.get('Inquiry_type'),
            'Inquiry_subject': request.data.get('Subject'),
            'Inquiry_main_content': request.data.get('Content')
        }

        inquiry_form = InquiryForm(inquiry_data)

        if inquiry_form.is_valid():
            inquiry_form.save()
            status = 'success'
        else:
            status = 'error'

    return Response({'status': status})