from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils import timezone
from datetime import timedelta
from datetime import datetime
import jwt
from django.contrib.humanize.templatetags.humanize import intcomma

# Rest
from rest_framework.decorators import api_view
from rest_framework.response import Response

from AuthUser.models import ServiceUser

# Donation Record
from .models import Membership_Article_Donation_Record
from .serializers import MembershipDonationRecordSerializer
from .forms import MembershipDonationWithdrawalRequestFrom

# Withdrawal Record
from .models import Membership_Donation_Withdrawal_Request
from .serializers import MembershipDonationWithdrawalSimpleSerializer
from .serializers import MembershipDonationWithdrawalDetailSerializer


# Global Function 
from Grainc.Global_Function.AuthControl import decodeUserToken


# Donation

@api_view(['GET'])
def GetDonationAmount(request):
    auth_header = request.headers.get('Authorization')
    if (auth_header):
        try:
            user_id = decodeUserToken(auth_header)
            user = ServiceUser.objects.get(id=user_id)
        except ServiceUser.DoesNotExist:
            return Response({'status': 'User Does not Exists'}, status=404)
        except jwt.ExpiredSignatureError:
            return Response({'status': 'Token expired'}, status=401)
        except jwt.InvalidTokenError:
            return Response({'status': 'Invalid token'}, status=401)
        
        if user.is_membership == False :
            return Response({'status': 'Not Membership'}, status=403)
        
        user_donation_amount = intcomma(user.membership_donation_cash)

        return Response(user_donation_amount)

    else:
        return Response({'status': 'Not Authorized'}, status=401)


@api_view(['GET'])
def GetUserDonationRecord(request):
    auth_header = request.headers.get('Authorization')
    if (auth_header):
        try:
            user_id = decodeUserToken(auth_header)
            user = ServiceUser.objects.get(id=user_id)
        except ServiceUser.DoesNotExist:
            return Response({'status': 'User Does not Exists'}, status=404)
        except jwt.ExpiredSignatureError:
            return Response({'status': 'Token expired'}, status=401)
        except jwt.InvalidTokenError:
            return Response({'status': 'Invalid token'}, status=401)
        
        if user.is_membership == False :
            return Response({'status': 'Not Membership'}, status=403)

    
        selected_date_range = request.GET.get('date_range')

        search_range_start_date = timezone.now() - timedelta(days=int(selected_date_range))
        search_range_end_date = timezone.now()

        record = Membership_Article_Donation_Record.objects.filter(
            donation_date__range = (search_range_start_date, search_range_end_date),
            article__author = user
        ).order_by('-donation_date')
        page = request.GET.get('page', 1)
        paginator = Paginator(record, 15)

        try:
            donation_record = paginator.page(page)
        except PageNotAnInteger:
            donation_record = paginator.page(1)
        except EmptyPage:
            donation_record = paginator.page(paginator.num_pages)

        record_serializer = MembershipDonationRecordSerializer(donation_record, many=True).data
    
        return Response({
            'record': record_serializer,
            'current_page': page,
            'max_page': paginator.num_pages,
            'start_date': search_range_start_date.strftime("%Y.%m.%d"),
            'end_date': search_range_end_date.strftime("%Y.%m.%d")
        })

    else:
        return Response({'status': 'not authorized'}, status=401)
    

@api_view(['POST'])
def HandleDonationWithdrawalRequest(request):
    auth_header = request.headers.get('Authorization')
    if (auth_header):
        try:
            user_id = decodeUserToken(auth_header)
            user = ServiceUser.objects.get(id=user_id)
        except ServiceUser.DoesNotExist:
            return Response({'status': 'User Does not Exists'}, status=404)
        except jwt.ExpiredSignatureError:
            return Response({'status': 'Token expired'}, status=401)
        except jwt.InvalidTokenError:
            return Response({'status': 'Invalid token'}, status=401)
        

        amount = request.data.get('amount')
        account_holder = request.data.get('account_holder')
        bank = request.data.get('bank')
        bank_code = request.data.get('bank_code')
        bank_account = request.data.get('bank_account')

        withdrawal_data = {
            'request_user': user,
            'amount': amount,
            'account_holder': account_holder,
            'bank': bank,
            'bank_code': bank_code,
            'bank_account': bank_account,
            'request_user_email': user.email
        }

        withdrawal_form = MembershipDonationWithdrawalRequestFrom(withdrawal_data)

        if withdrawal_form.is_valid():
            try: 
                if (user.membership_donation_cash >= int(amount)):
                    user.membership_donation_cash -= int(amount)
                else:
                    return Response({'status', 'donation money is not enough'}, status=403)
            except:
                return Response({'status', 'user cash discount error'}, status=404)
            
            withdrawal_form.save()
            user.save()

            return Response({'status': 'withdrawal requested'}, status=200)
        else:
            return Response({'status': 'withdrawal form error'}, status=404)
    else:
        return Response({'status': 'not authorized'}, status=401)
    

@api_view(['GET'])
def GetDonationWithdrawalHistory(request):
    auth_header = request.headers.get('Authorization')
    if (auth_header):
        try:
            user_id = decodeUserToken(auth_header)
            user = ServiceUser.objects.get(id=user_id)
        except ServiceUser.DoesNotExist:
            return Response({'status': 'User Does not Exists'}, status=404)
        except jwt.ExpiredSignatureError:
            return Response({'status': 'Token expired'}, status=401)
        except jwt.InvalidTokenError:
            return Response({'status': 'Invalid token'}, status=401)
        
        if (user.is_membership == False):
            return Response({'status': 'Not Membership'}, status=403)
        
            
        selected_date_range = request.GET.get('date_range')

        search_range_start_date = timezone.now() - timedelta(days=int(selected_date_range))
        search_range_end_date = timezone.now()


        record = Membership_Donation_Withdrawal_Request.objects.filter(
            request_date__range = (search_range_start_date, search_range_end_date),
            request_user = user
        ).order_by('-request_date')
        page = request.GET.get('page', 1)
        paginator = Paginator(record, 15)

        try:
            withdrawal_record = paginator.page(page)
        except PageNotAnInteger:
            withdrawal_record = paginator.page(1)
        except EmptyPage:
            withdrawal_record = paginator.page(paginator.num_pages)

        record_serializer = MembershipDonationWithdrawalSimpleSerializer(withdrawal_record, many=True)

        return Response({
            'record': record_serializer.data,
            'current_page': page,
            'max_page': paginator.num_pages,
            'start_date': search_range_start_date.strftime("%Y.%m.%d"),
            'end_date': search_range_end_date.strftime("%Y.%m.%d")
        })
        
    else:
        return Response({'status': 'not authorized'}, status=401)


@api_view(['GET'])
def GetDonationWithdrawalHistoryDetail(request, record_id):
    auth_header = request.headers.get('Authorization')
    if (auth_header):
        try:
            user_id = decodeUserToken(auth_header)
            user = ServiceUser.objects.get(id=user_id)
            withdrawal_history = Membership_Donation_Withdrawal_Request.objects.get(id=record_id)

        except ServiceUser.DoesNotExist:
            return Response({'status': 'User Does not Exists'}, status=404)
        except Membership_Donation_Withdrawal_Request.DoesNotExist:
            return Response({'status': 'Record Does not Exists'}, status=404)
        except jwt.ExpiredSignatureError:
            return Response({'status': 'Token expired'}, status=401)
        except jwt.InvalidTokenError:
            return Response({'status': 'Invalid token'}, status=401)
        

        if user != withdrawal_history.request_user:
            return Response({'status': 'Not authorized'}, status=403)
        else:
            history_serializer = MembershipDonationWithdrawalDetailSerializer(withdrawal_history)
            return Response (history_serializer.data)
        
    else:
        return Response({'status': 'not authorized'}, status=401)
