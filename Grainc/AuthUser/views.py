import requests
from django.contrib.auth import authenticate
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from datetime import timedelta
from datetime import timezone as dt_timezone
from django.utils import timezone
from django.conf import settings
import random
from django.db import transaction, IntegrityError
from django.db.utils import OperationalError
from django.core.files.base import ContentFile
from django.contrib.humanize.templatetags.humanize import intcomma

# Query Optimization
from django.db.models import Prefetch

#global function
from Grainc.Global_Function.AuthControl import decodeUserToken
from Grainc.Global_Function.ImgProcessorQuill import QuillContentDelete
from Grainc.Global_Function.ImgProcessorQuill import compress_image, compress_image_flutter

# Social Login
# profile image
from django.core.files.uploadedfile import InMemoryUploadedFile
from io import BytesIO


from .forms import SellReportsSocialAccountCreationFrom
from json.decoder import JSONDecodeError

# JWT
import jwt
from rest_framework_simplejwt.tokens import RefreshToken, BlacklistedToken, OutstandingToken
from rest_framework_simplejwt.views import TokenObtainPairView,TokenRefreshView
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from . serializers import MyTokenObtainPairSerializer

# For email
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
import threading

# For Community Article Delete

# Signup
from .forms import SellReportsUserCreationForm

#Global user information
from .serializers import GlobalUserInformationSerializer
from .models import ServiceUser

#User Profile
from .serializers import UserProfileSerializer

#Community
from Community.models import Community_Articles

#MyPage
# My Profile
from .serializers import MyPageProfileSerializer
from Community.serializers import MyPageCommunityArticleSerializer
from Transaction.models import Membership_Article_Donation_Record
# My Profile Flutter start api
from Community.serializers import MyProfileCommunityArticleSerializer

# Subscribing content 
from Community.serializers import CommunityArticleSerializers
from Community.views import CommunityArticleSerializerPR, CommunityArticleSerializerSR

# Account Cancel Survey From 
from Survey.forms import SurveyForm

# Create your views here.

# simple login
class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


class CustomTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response({'detail': 'Refresh token is required'}, status=400)

        # Attempt to decode the refresh token
        try:
            decoded = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=['HS256'])
            decoded_jti = decoded.get('jti')
            user_id = decoded.get('user_id')  # Get user_id for later use

            # Check if the refresh token exists in OutstandingToken
            try:
                token = OutstandingToken.objects.get(jti=decoded_jti)

                # Check if the token is blacklisted
                if BlacklistedToken.objects.filter(token=token).exists():
                    return Response({'detail': 'Token has been blacklisted'}, status=401)

                # Check expiration of the refresh token
                token_expiration_time = timezone.datetime.fromtimestamp(decoded.get('exp'), dt_timezone.utc)
                if token_expiration_time < timezone.now():
                    # Blacklist the expired token and return an error response
                    BlacklistedToken.objects.create(token=token)
                    return Response({'detail': 'Refresh token has expired'}, status=401)

            except OutstandingToken.DoesNotExist:
                return Response({'detail': 'Invalid or expired token'}, status=400)

            # Call the parent method to get the response for a valid refresh token
            response = super().post(request, *args, **kwargs)

            # Update last active date if a new token is issued
            if response.status_code == 200 and user_id:
                user = ServiceUser.objects.get(id=user_id)
                user.last_active_date = timezone.now()
                user.save()

            return response

        except jwt.ExpiredSignatureError:
            return Response({'detail': 'Refresh token has expired'}, status=401)
        except jwt.DecodeError:
            return Response({'detail': 'Token decode error'}, status=400)
        except ServiceUser.DoesNotExist:
            return Response({'detail': 'User not found'}, status=404)
# Social Login



@transaction.atomic
def social_account_creation(email, profile_image_url, provider, social_account_detail):

    if ServiceUser.objects.filter(email=email).exists():
        raise ValueError(f"User with email {email} already exists")

    social_account_data = {
        'email': email,
        'social_account_provider': provider,
        'social_account_detail': social_account_detail,
    }
    social_account_form = SellReportsSocialAccountCreationFrom(social_account_data)
    if social_account_form.is_valid():
        user = social_account_form.social_account_setup()
        if profile_image_url:
            try:
                profile_image_response = requests.get(profile_image_url)
                if profile_image_response.status_code == 200:
                    profile_image = profile_image_response.content
                    compressed_profile_image = compress_image(profile_image)
                    compressed_profile_image_file = ContentFile(compressed_profile_image, name='profile_image.jpg')
                    user.profile_image = compressed_profile_image_file
            except Exception as e:
                print(f"Error processing profile image: {e}")
        user.save()
        return user
    else:
        print(social_account_form.errors)
        return None




def social_account_token_issue(user):
    access_token = MyTokenObtainPairSerializer.get_token(user).access_token
    refresh_token = MyTokenObtainPairSerializer.get_token(user)
    token_data = {
        'access': str(access_token),  # Convert AccessToken to string
        'refresh': str(refresh_token),  # Convert RefreshToken to string
    }

    return token_data

BASE_URL_REACT = 'http://localhost:3000'
BASE_URL_DJANGO = 'http://localhost:8000'
GOOGLE_CALLBACK_URL = BASE_URL_REACT + '/login/google/callback'
NAVER_CALLBACK_URI = BASE_URL_REACT + '/login/naver/callback'
KAKAO_CALLBACK_URI = BASE_URL_REACT + '/login/kakao/callback'
state = getattr(settings, 'STATE')
#http://localhost:8000/login/google/callback
@api_view(['GET'])
def google_login(request):
    """
    Code Request
    """
    scope = "https://www.googleapis.com/auth/userinfo.email"
    client_id = getattr(settings, "SOCIAL_AUTH_GOOGLE_CLIENT_ID")
    return Response({
        'login_link' : f"https://accounts.google.com/o/oauth2/v2/auth?client_id={client_id}&response_type=code&redirect_uri={GOOGLE_CALLBACK_URL}&scope={scope}"
    }, status=200)

@api_view(['POST'])
def google_callback(request):
    """
    Access Token handel in React

    """
    access_token = request.data.get('access_token')

    """
    Email Request

    """
    user_info = requests.get(
        f"https://www.googleapis.com/oauth2/v1/tokeninfo?access_token={access_token}")
    user_info_status = user_info.status_code
    if user_info_status != 200:
        return Response({'err_msg': 'failed to get email'})
    user_info_json = user_info.json()
    email = user_info_json.get('email')

    """
    Signup or Signin Request <---- 소셜 Model에 추가 X 기존 로그인 통합

    """

    try:
        user = ServiceUser.objects.get(email=email)
        # 기존에 가입된 유저의 Provider가 google이 아니면 에러 발생, 맞으면 로그인
        if user.social_account_provider != 'google':
            if user.social_account_provider:
                provider = user.social_account_provider
            else:
                provider = 'email'
            return Response({
                'status': 'wrong_provider',
                'provider': provider,
                'userEmail': email
            } , status=404)
        
        token_data = social_account_token_issue(user)
        return Response({
            'AuthToken': token_data,
            'UsernameRequired': False
        }, status=200)
      
    except ServiceUser.DoesNotExist:
        profile_image = None
        with transaction.atomic():
            if (email):
                user = social_account_creation(email, profile_image, 'google', user_info_json)
                if user:
                    token_data = social_account_token_issue(user)
                    return Response({
                        'AuthToken': token_data,
                        'UsernameRequired': True
                    }, status=200)
                else:
                    return Response({'err_msg': 'Failed to create new user account.'}, status=400) 
    except IntegrityError:
        return Response({'err_msg': 'Integrity error, possible duplicate entry.'}, status=400)
    except OperationalError:
        return Response({'err_msg': 'Database is currently busy, try again later.'}, status=500)
    except Exception as e:
        return Response({'err_msg': f'Unexpected error: {str(e)}'}, status=500)
    
@api_view(['POST'])
def google_callback_mobile(request):
    email = request.data.get('email')
    if (email): 
        try:
            user = ServiceUser.objects.get(email=email)
            # 기존에 가입된 유저의 Provider가 google이 아니면 에러 발생, 맞으면 로그인
            if user.social_account_provider != 'google':
                if user.social_account_provider:
                    provider = user.social_account_provider
                else:
                    provider = 'email'
                return Response({
                    'status': 'wrong_provider',
                    'provider': provider,
                    'userEmail': email
                } , status=403)
            
            token_data = social_account_token_issue(user)
            return Response({
                'AuthToken': token_data,
                'UsernameRequired': False
            }, status=200)
        
        except ServiceUser.DoesNotExist:
            profile_image = None
            with transaction.atomic():
                if (email):
                    user = social_account_creation(email, profile_image, 'google', 'google_social_login_mobile')
                    if user:
                        token_data = social_account_token_issue(user)
                        return Response({
                            'AuthToken': token_data,
                            'UsernameRequired': True
                        }, status=200)
                    else:
                        return Response({'err_msg': 'Failed to create new user account.'}, status=400) 
        except IntegrityError:
            return Response({'err_msg': 'Integrity error, possible duplicate entry.'}, status=400)
        except OperationalError:
            return Response({'err_msg': 'Database is currently busy, try again later.'}, status=500)
        except Exception as e:
            return Response({'err_msg': f'Unexpected error: {str(e)}'}, status=500)
        
    else:
        return Response({'status': 'email not provided'}, status=404)

@api_view(['GET'])
def naver_login(request):
    client_id = getattr(settings, "SOCIAL_AUTH_NAVER_CLIENT_ID")
    return Response({
        'login_link' : f"https://nid.naver.com/oauth2.0/authorize?response_type=code&client_id={client_id}&state=1234&redirect_uri={NAVER_CALLBACK_URI}"
    }, status=200)

@api_view(['POST'])
def naver_callback(request):

    code = request.data.get('code')
    state = request.data.get('state')

    client_id = getattr(settings, "SOCIAL_AUTH_NAVER_CLIENT_ID")
    client_secret = getattr(settings, "REACT_APP_SOCIAL_AUTH_NAVER_SECRET")

    token_request = requests.get(f"https://nid.naver.com/oauth2.0/token?grant_type=authorization_code&client_id={client_id}&client_secret={client_secret}&code={code}&state={state}")
    token_json = token_request.json()

    access_token = token_json.get("access_token")
    profile_request = requests.get("https://openapi.naver.com/v1/nid/me", headers={"Authorization" : f"Bearer {access_token}"},)
    profile_data = profile_request.json()

    email = profile_data.get('response', {}).get('email')

    try:
        user = ServiceUser.objects.get(email=email)
        # 기존에 가입된 유저의 Provider가 google이 아니면 에러 발생, 맞으면 로그인
        if user.social_account_provider != 'naver':
            if user.social_account_provider:
                provider = user.social_account_provider
            else:
                provider = 'email'
            return Response({
                'status': 'wrong_provider',
                'provider': provider,
                'userEmail': email
            } , status=404)
        
        token_data = social_account_token_issue(user)

        # First Time UserName Registration

        return Response({
            'AuthToken': token_data,
            'UsernameRequired': False
        }, status=200)

    except ServiceUser.DoesNotExist:
        # 기존에 가입된 유저가 없으면 새로 가입
        profile_image = profile_data.get('response', {}).get('profile_image')
        try:
            with transaction.atomic():
                if (email):
                    user = social_account_creation(email, profile_image, 'naver', profile_data)
                    if user:
                        token_data = social_account_token_issue(user)
                        return Response({
                            'AuthToken': token_data,
                            'UsernameRequired': True
                        }, status=200)
                    else:
                        return Response({'err_msg': 'Failed to create new user account.'}, status=400)
        except IntegrityError:
            return Response({'err_msg': 'Integrity error, possible duplicate entry.'}, status=400)
        except OperationalError:
            return Response({'err_msg': 'Database is currently busy, try again later.'}, status=500)
        except Exception as e:
            return Response({'err_msg': f'Unexpected error: {str(e)}'}, status=500)


@api_view(['POST'])
def naver_callback_mobile(request):
    email = request.data.get('email')
    if (email):
        try:
            user = ServiceUser.objects.get(email=email)
            # 기존에 가입된 유저의 Provider가 google이 아니면 에러 발생, 맞으면 로그인
            if user.social_account_provider != 'naver':
                if user.social_account_provider:
                    provider = user.social_account_provider
                else:
                    provider = 'email'
                return Response({
                    'status': 'wrong_provider',
                    'provider': provider,
                    'userEmail': email
                } , status=403)
            
            token_data = social_account_token_issue(user)

            # First Time UserName Registration

            return Response({
                'AuthToken': token_data,
                'UsernameRequired': False
            }, status=200)
        
        except ServiceUser.DoesNotExist:
            profile_image = request.data.get('profile_image')
            try:
                with transaction.atomic():
                    if (email):
                        user = social_account_creation(email, profile_image, 'naver', 'naver account created from mobile')
                        if user:
                            token_data = social_account_token_issue(user)
                            return Response({
                                'AuthToken': token_data,
                                'UsernameRequired': True
                            }, status=200)
                        else:
                            return Response({'err_msg': 'Failed to create new user account.'}, status=400)
            except IntegrityError:
                return Response({'err_msg': 'Integrity error, possible duplicate entry.'}, status=400)
            except OperationalError:
                return Response({'err_msg': 'Database is currently busy, try again later.'}, status=500)
            except Exception as e:
                return Response({'err_msg': f'Unexpected error: {str(e)}'}, status=500)

    return Response({'status': 'User Email Is not provided'}, status=404)


@api_view(['GET'])
def kakao_login(request):
    rest_api_key = getattr(settings, "SOCIAL_AUTH_KAKAO_REST_API_KEY")
    return Response({
        'login_link' : f"https://kauth.kakao.com/oauth/authorize?client_id={rest_api_key}&redirect_uri={KAKAO_CALLBACK_URI}&response_type=code"
    })

@api_view(['POST'])
def kakao_callback(request):

    access_token = request.data.get('access_token')
    """
    Email Request
    """
    profile_request = requests.get(
        "https://kapi.kakao.com/v2/user/me", headers={"Authorization": f"Bearer {access_token}"})
    profile_json = profile_request.json()
    error = profile_json.get("error")
    if error is not None:
        raise JSONDecodeError(error)
    kakao_account = profile_json.get('kakao_account')
    """
    kakao_account에서 이메일 외에
    카카오톡 프로필 이미지, 배경 이미지 url 가져올 수 있음
    print(kakao_account) 참고
    """
    # print(kakao_account)
    email = kakao_account.get('email')
    
    try:
        user = ServiceUser.objects.get(email=email)
        # 기존에 가입된 유저의 Provider가 kakao가 아니면 에러 발생, 맞으면 로그인
        if user.social_account_provider != 'kakao':
            if user.social_account_provider:
                provider = user.social_account_provider
            else:
                provider = 'email'
            return Response({
                'status': 'wrong_provider',
                'provider': provider,
                'userEmail': email
            } , status=404)
        
        token_data = social_account_token_issue(user)
        return Response({
            'AuthToken': token_data,
            'UsernameRequired': False
        }, status=200)
        # Token Obtain
    except ServiceUser.DoesNotExist:
        # 기존에 가입된 유저가 없으면 새로 가입
        profile_image = kakao_account.get('profile', {}).get('profile_image_url')
        try:
            with transaction.atomic():
                if (email):
                    user = social_account_creation(email, profile_image, 'kakao', kakao_account)
                    if user:
                        token_data = social_account_token_issue(user)
                        return Response({
                            'AuthToken': token_data,
                            'UsernameRequired': True
                        }, status=200)
                    else:
                        return Response({'err_msg': 'Failed to create new user account.'}, status=400)
        except IntegrityError:
            return Response({'err_msg': 'Integrity error, possible duplicate entry.'}, status=400)
        except OperationalError:
            return Response({'err_msg': 'Database is currently busy, try again later.'}, status=500)
        except Exception as e:
            return Response({'err_msg': f'Unexpected error: {str(e)}'}, status=500)

@api_view(['POST'])
def kakao_callback_mobile(request):
    email = request.data.get('email')
    if(email):
        try:
            user = ServiceUser.objects.get(email=email)
            # 기존에 가입된 유저의 Provider가 kakao가 아니면 에러 발생, 맞으면 로그인
            if user.social_account_provider != 'kakao':
                if user.social_account_provider:
                    provider = user.social_account_provider
                else:
                    provider = 'email'
                return Response({
                    'status': 'wrong_provider',
                    'provider': provider,
                    'userEmail': email
                } , status=403)
            
            token_data = social_account_token_issue(user)
            return Response({
                'AuthToken': token_data,
                'UsernameRequired': False
            }, status=200)
            # Token Obtain
        except ServiceUser.DoesNotExist:
            # 기존에 가입된 유저가 없으면 새로 가입
            profile_image = request.data.get('profile_image_url')
            try:
                with transaction.atomic():
                    if (email):
                        user = social_account_creation(email, profile_image, 'kakao', 'kakao_social_mobile')
                        if user:
                            token_data = social_account_token_issue(user)
                            return Response({
                                'AuthToken': token_data,
                                'UsernameRequired': True
                            }, status=200)
                        else:
                            return Response({'err_msg': 'Failed to create new user account.'}, status=400)
            except IntegrityError:
                return Response({'err_msg': 'Integrity error, possible duplicate entry.'}, status=400)
            except OperationalError:
                return Response({'err_msg': 'Database is currently busy, try again later.'}, status=500)
            except Exception as e:
                return Response({'err_msg': f'Unexpected error: {str(e)}'}, status=500)
    else:
        return Response({'status': 'user email not provided'}, status=404)

@api_view(['POST'])
def SocialLoginUsernameRegistration(request):
    auth_header = request.headers.get('Authorization')
    
    if not auth_header:
        return Response({'status': 'Authorization header missing'}, status=400)
    
    if request.method != 'POST':
        return Response({'status': 'wrong_request'}, status=400)

    try:
        # Decode user token
        user_id = decodeUserToken(auth_header)
        user = ServiceUser.objects.get(id=user_id)

        username = request.data.get('username')
        if not username:
            return Response({'status': 'Username is required'}, status=400)
        
        if ServiceUser.objects.filter(username=username).exists():
            return Response({'status': 'username is taken'}, status=404)

        if user.is_social_account:
            user.username = username
            user.save()
            return Response({'status': 'Username updated successfully'}, status=200)
        else:
            return Response({'status': 'Not a social account'}, status=400)

    except ServiceUser.DoesNotExist:
        return Response({'status': 'User does not exist'}, status=404)

    except jwt.ExpiredSignatureError:
        return Response({'status': 'Token expired'}, status=401)

    except jwt.InvalidTokenError:
        return Response({'status': 'Invalid token'}, status=401)

    except Exception as e:
        return Response({'status': 'Internal server error'}, status=500)


    
@api_view(['POST'])
def SellReportAccountCreation(request):
    if request.method == "POST":
        user_creation_form = SellReportsUserCreationForm(request.data)
        if user_creation_form.is_valid():
            user_creation_form.save()

            #Send mail verification
            user_email = request.data.get('email')

            # Get User and encode user id with base64 for email verification
            authenticate_requested_user = ServiceUser.objects.get(email=user_email)
            # Email verification expire date time setting
            authenticate_requested_user.email_verification_link_generated_at = timezone.now()
            #Create Verification Code
            verification_code = random.randint(100000, 999999)
            authenticate_requested_user.signup_verification_code = verification_code
            authenticate_requested_user.save()

            # Define email subject, from, and to addresses
            subject = '셀리포트 이메일 인증'
            from_email = f'셀리포트 <{settings.DEFAULT_FROM_MAIL}>'
            to = [user_email]

            html_content = render_to_string('Email_Verification_Email.html', {'verification_code': verification_code})

            # Create EmailMessage object
            email = EmailMessage(subject=subject, body=html_content, from_email=from_email, to=to)
            email.content_subtype = "html"  # Set the content subtype to "html"

            # Send email
            threading.Thread(target=email.send).start()

            return Response({'status': 'account_created'})
        else:
            return Response({'status': 'signup_error'})
        

@api_view(['POST'])
def signup_email_authentication(request):
    if request.method == 'POST':
        verifying_email = request.data.get('verifying_email')
        verification_code = request.data.get('verification_code')
        
        try:
            requested_user = ServiceUser.objects.get(email=verifying_email)
        except ServiceUser.DoesNotExist:
            return Response({'status': 'user not found'}, status=404)
        
        link_generated_at = requested_user.email_verification_link_generated_at
        expiration_time = link_generated_at + timedelta(hours=1)  # Assuming link expires after 1 hour

        if timezone.now() <= expiration_time:
            if not requested_user.is_active:
                if requested_user.signup_verification_code == int(verification_code):
                    requested_user.is_active = True
                    requested_user.save()
                    return Response({'status': 'signup_complete'}, status=200)
                else:
                    return Response({'status': '인증코드가 일치하지 않습니다'}, status=400)
            else:
                return Response({'status': '인증완료'}, status=400)
        else:
            requested_user.delete()
            return Response({'status': '인증시간이 만료되없습니다'}, status=400)
                

@api_view(['POST'])
def SignupEmailCheck(request):
    email = request.data.get('email')

    try:
        check_email = ServiceUser.objects.get(email=email)
        email_error = True
    except ServiceUser.DoesNotExist:
        email_error = False

    return Response({'email_error': email_error})



@api_view(['POST'])
def UsernameErrorCheck(request):
    username = request.data.get('username')

    try:
        check_username = ServiceUser.objects.get(username=username)
        username_error = True
    except ServiceUser.DoesNotExist:
        username_error = False

    return Response({'username_error': username_error})


@api_view(['POST'])
def PasswordResetRequest(request):
    if request.method == 'POST':
        user_email = request.data.get('email')

        try:
            user = ServiceUser.objects.get(email=user_email)
            if user.social_account_provider:
                provider = user.social_account_provider
            else:
                provider = 'email'

            if user.is_social_account == True:
                return Response({
                    'status': 'wrong_provider',
                    'provider': provider,
                }, status=403)


            else:
                # Get User and encode user id with base64 for email verification
                authenticate_requested_user = ServiceUser.objects.get(email=user_email)
                # Email verification expire date time setting
                authenticate_requested_user.password_reset_link_generated_at = timezone.now()
                #Create Verification Code
                verification_code = random.randint(100000, 999999)
                authenticate_requested_user.password_reset_verification_code = verification_code
                authenticate_requested_user.save()

                # Define email subject, from, and to addresses
                subject = '셀리포트 이메일 인증'
                from_email = f'셀리포트 <{settings.DEFAULT_FROM_MAIL}>'
                to = [user_email]

                html_content = render_to_string('Password_Reset_Email.html', {'verification_code': verification_code})

                # Create EmailMessage object
                email = EmailMessage(subject=subject, body=html_content, from_email=from_email, to=to)
                email.content_subtype = "html"  # Set the content subtype to "html"

                # Send email
                threading.Thread(target=email.send).start()

                return Response({'status': 'password reset link sent'}, status=200)
        except ServiceUser.DoesNotExist:
            return Response({'status': 'user does not exist'}, status=404)
    
    else:
        return Response({'status': 'wrong request'}, status=400)



@api_view(['POST'])
def password_reset_authentication(request):
    try:
        type = request.data.get('type')
        verification_code = request.data.get('verification_code')
        int_verification_code = int(verification_code)
        email = request.data.get('email')
        requested_user = ServiceUser.objects.get(email=email)
    except (TypeError, ValueError, OverflowError, ServiceUser.DoesNotExist):
        return Response({'status' : 'token fail'}, status=404)

    if requested_user:
        reset_link_generated_at = requested_user.password_reset_link_generated_at
        expiration_time = reset_link_generated_at + timedelta(minutes=10)  

        if type == 'verification':
            if reset_link_generated_at and verification_code is not None:
                if timezone.now() <= expiration_time:
                    if requested_user.password_reset_verification_code == int_verification_code:
                        return Response({'status': 'continue password reset'}, status=200)  
                    else:
                        return Response({'message': '인증코드를 다시 확인해주세요'}, status=403)              
                else:
                    return Response({'message': '인증 시간이 초과 되었습니다'}, status=404)
        elif type == 'password_change':
            if requested_user.password_reset_verification_code == int_verification_code:
                new_password = request.data.get('password')
                requested_user.set_password(new_password)
                if not requested_user.is_active: # 만약에 회원가입후 이메일 인증을 까먹었을때
                    requested_user.is_active = True
                requested_user.save()
                return Response({'status': 'password changed'}, status=200) 
            else:
                return Response({'message': '인증코드를 다시 확인해주세요'}, status=403) 

    return Response({'status': 'fail password reset'}, status=404)          


#Global Subscribe Feature

# deprecated
@api_view(['GET']) 
def CheckUserSubscriberCommunity(request, article_id, user_id):
    try:
        user = ServiceUser.objects.get(id=user_id)
    except ServiceUser.DoesNotExist:
        return Response({'status': 'failed to find user'}, status=404)
    
    try:
        selected_article = Community_Articles.objects.get(id=article_id)
    except Community_Articles.DoesNotExist:
        return Response({'status': 'article does not exist'}, status=404)
    
    finding_user = selected_article.author

    subscribe_status = finding_user in user.subscribing_user.all()

    return Response({'status': subscribe_status})



@api_view(['POST'])
def HandelSubscribingFeatureCommunity(request):
    try:
        user_id = request.data.get('user_id')
        user = ServiceUser.objects.get(id=user_id)
    except ServiceUser.DoesNotExist:
        return Response({'status': 'user does not exist'})
    
    try:
        article_id = request.data.get('article_id')
        selected_article = Community_Articles.objects.get(id=article_id)
        target_user = selected_article.author
    except Community_Articles.DoesNotExist:
        return Response({'status': 'article does not exist'})
    
    if target_user in user.subscribing_user.all():
        user.subscribing_user.remove(target_user)
        target_user.subscribing_user.remove(user)
        status = 'subscribed'
    else:
        user.subscribing_user.add(target_user)
        target_user.subscribing_user.add(user)
        status = 'unsubscribed'

    user.save()
    target_user.save()
    return Response({'status': status})


# deprecated
@api_view(['GET'])
def ProfileSubscribeStatusCheck(request, authUser_id, user_id):
    try:
        user = ServiceUser.objects.get(id=authUser_id)
    except ServiceUser.DoesNotExist:
        return Response({'status': 'authUser does not exist'})
    
    try:
        targetUser = ServiceUser.objects.get(id=user_id)
    except ServiceUser.DoesNotExist:
        return Response({'status': 'Target user does not exist'})
    
    
    subscribe_status = targetUser in user.subscribing_user.all()
    return Response({'status': subscribe_status})

@api_view(['POST'])
def HandelSubscribingFeatureProfile(request):
    try:
        authUser_id = request.data.get('authUser_id')
        user = ServiceUser.objects.get(id=authUser_id)
    except ServiceUser.DoesNotExist:
        return Response({'status': 'user does not exist'})
    
    try:
        user_id = request.data.get('user_id')
        targetUser = ServiceUser.objects.get(id=user_id)
    except ServiceUser.DoesNotExist:
        return Response({'status': 'user does not exist'})

    subscribe_status = user.subscribing_user.filter(id=targetUser.id).exists()

    if subscribe_status:
        targetUser.subscribers.remove(user)
        user.subscribing_user.remove(targetUser)
        status = 'subscribed'
    else:
        targetUser.subscribers.add(user)
        user.subscribing_user.add(targetUser)
        status = 'unsubscribed'

    return Response({'status': status})




# Global User State Management

@api_view(['GET'])
def GetUserProfileImage(request, user_id):
    try:
        user = ServiceUser.objects.get(id=user_id)

        user_profile_image = user.profile_image.url
        return Response({'profile_image_data': user_profile_image})
    except:
        return Response({'status': 'profile image does not exists'}, status=404)


# User Profile 
@api_view(['GET'])
def GetUserProfileInformation(request, user_id):
    try:
        user = ServiceUser.objects.get(id=user_id)
    except ServiceUser.DoesNotExist:
        return Response({'status': 'user does not exist'})
        
    serializer = UserProfileSerializer(user)
    return Response(serializer.data)


@api_view(['GET'])
def MyPageGetUserProfileInformation(request, user_id):
    try:
        user = ServiceUser.objects.get(id=user_id)
    except ServiceUser.DoesNotExist:
        return Response({'status': 'user does not exist'})
    
    
    return Response({
        'like_count': intcomma(user.likes_count),
        'article_count': intcomma(user.article_count),
        'subscriber_count': intcomma(user.subscribers.count()),
    })


# -------------- Subscribing Contents

@api_view(['GET'])
def getUserSubscribingContents(request):
    auth_header = request.headers.get('Authorization')
    if (auth_header):
        try:
            user_id = decodeUserToken(auth_header)
            user = ServiceUser.objects.get(id=user_id)
        except ServiceUser.DoesNotExist:
            return Response({'status': 'user does not exist'})
        except jwt.ExpiredSignatureError:
            return Response({'status': 'Token expired'}, status=401)
        except jwt.InvalidTokenError:
            return Response({'status': 'Invalid token'}, status=401)
        
        subscribing_contents = []
        subscribing_users = user.subscribing_user.all()

        one_month_ago = timezone.now() - timedelta(days=90)

        for users in subscribing_users:
            selected_articles = Community_Articles.objects.select_related(
                *CommunityArticleSerializerSR
            ).prefetch_related(
                *CommunityArticleSerializerPR
            ).filter(
                author=users, 
                create_date__gte=one_month_ago,
                saved_article = False
            ).order_by('-create_date')
            for articles in selected_articles:
                subscribing_contents.append(articles)

        page = request.GET.get('page')
        paginator = Paginator(subscribing_contents, 15)
        
        try:
            articles = paginator.page(page)
        except PageNotAnInteger:
            articles = paginator.page(1)
        except EmptyPage:
            articles = paginator.page(paginator.num_pages)

        serializer = CommunityArticleSerializers(articles, many=True, context={'user': user})
        return Response({
            'articles': serializer.data,
            'current_page': page,
            'max_page': paginator.num_pages
        })    
    else:
        return Response({'status': 'not authorized'}, status=401)
    
    
@api_view(['GET'])
def getUserSubscribingUsers(request):
    auth_header = request.headers.get('Authorization')
    if (auth_header):
        try:
            user_id = decodeUserToken(auth_header)
            user = ServiceUser.objects.prefetch_related(
                Prefetch(
                    'subscribing_user',
                    queryset=ServiceUser.objects.only(
                        'username',
                        'pk',
                        'profile_image'
                    )
                )
            ).get(id=user_id)
        except ServiceUser.DoesNotExist:
            return Response({'status': 'user does not exist'})
        except jwt.ExpiredSignatureError:
            return Response({'status': 'Token expired'}, status=401)
        except jwt.InvalidTokenError:
            return Response({'status': 'Invalid token'}, status=401)
        
        subscribing_users = user.subscribing_user.all()

        page = request.GET.get('page')
        paginator = Paginator(subscribing_users, 15)
        
        try:
            users = paginator.page(page)
        except PageNotAnInteger:
            users = paginator.page(1)
        except EmptyPage:
            users = paginator.page(paginator.num_pages)

        serializer = GlobalUserInformationSerializer(users, many=True)

        return Response({
            'users': serializer.data,
            'current_page': page,
            'max_page': paginator.num_pages
        })    
    else:
        return Response({'status': 'not authorized'}, status=401)



# !!!!!!!!!!!!!!!!!!!!!!! All Transaction Related My Page Views are in Transaction App !!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# My Profile



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def PostNewProfileImage(request):
    auth_header = request.headers.get('Authorization')
    try:
        user_id = decodeUserToken(auth_header)
        user = ServiceUser.objects.get(id=user_id)
        new_profile_image = request.FILES.get('profile_image')
        
        if new_profile_image:
            try:
                # Compress image if in memory
                if isinstance(new_profile_image, InMemoryUploadedFile):
                    compressed_image = compress_image_flutter(new_profile_image)
                else:
                    compressed_image = compress_image(new_profile_image)
                
                # Create a new InMemoryUploadedFile with the compressed image
                new_image_file = InMemoryUploadedFile(
                    file=BytesIO(compressed_image),
                    field_name='profile_image',  # The field name in the model
                    name='profile_image.jpg',    # Set a static name for the file
                    content_type=new_profile_image.content_type,
                    size=len(compressed_image),
                    charset=None
                )
                
                # Overwrite the S3 file while preserving the URL
                user.profile_image.delete(save=False)  # Deletes the old file on S3
                user.profile_image = new_image_file
                print(1)
                user.save()
                
                return Response({'status': 'Profile image updated successfully'}, status=200)

            except Exception as e:
                print(f"Error updating profile image: {e}")
                return Response({'status': 'Error processing image'}, status=500)
        else:
            return Response({'status': 'Error no images found'}, status=404)

    except jwt.ExpiredSignatureError:
        return Response({'status': 'Token expired'}, status=401)
    except jwt.InvalidTokenError:
        return Response({'status': 'Invalid token'}, status=401)

@api_view(['POST'])
def ModifyUserProfile(request):
    auth_header = request.headers.get('Authorization')
    try:
        user_id = decodeUserToken(auth_header)
        user = ServiceUser.objects.get(id=user_id)
        new_introduction = request.data.get('newIntroduction')
        new_username = request.data.get('newUsername')
        new_donation_message = request.data.get('newDonationMessage')
        if new_introduction:
            if new_introduction:
                user.introduction = new_introduction

        if new_username and user.username != new_username:
            if ServiceUser.objects.filter(username=new_username).exists():
                return Response({'status': 'username taken'}, status=409)
            else:
                user.username = new_username

        user.donation_message = new_donation_message
        

        user.save()

        # Generate new tokens using the custom serializer
        refresh = RefreshToken.for_user(user)
        access_token = MyTokenObtainPairSerializer.get_token(user).access_token

        data = {
            'refresh': str(refresh),  # Convert RefreshToken to string
            'access': str(access_token),  # Convert AccessToken to string
        }
        return Response(data, status=200)
    
    except jwt.ExpiredSignatureError:
        return Response({'status': 'Token expired'}, status=401)
    except jwt.InvalidTokenError:
        return Response({'status': 'Invalid token'}, status=401)
    
@api_view(['POST'])
def MyPagePasswordChange(request):
    auth_header = request.headers.get('Authorization')
    if request.method == 'POST':
        try:
            user_id = decodeUserToken(auth_header)
            user = ServiceUser.objects.get(id=user_id)

            current_password = request.data.get('current_password')
            new_password = request.data.get('new_password')

            if user.check_password(current_password):
                user.set_password(new_password)
                user.save()
                return Response({'status': '비밀번호 변경완료'}, status=200)
            else:
                return Response({'status': '비밀번호가 일치하지 않습니다'}, status=400)

        except jwt.ExpiredSignatureError:
            return Response({'status': 'Token expired'}, status=401)
        except jwt.InvalidTokenError:
            return Response({'status': 'Invalid token'}, status=401)
    
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def GetMyPageProfileData(request):
    auth_header = request.headers.get('Authorization')
    try:
        user_id = decodeUserToken(auth_header)
        user = ServiceUser.objects.get(id=user_id)

        serializer = MyPageProfileSerializer(user)

        return Response(serializer.data)
        

    except ServiceUser.DoesNotExist:
        return Response({'status': 'User Does not Exists'}, status=404)
    except jwt.ExpiredSignatureError:
        return Response({'status': 'Token expired'}, status=401)
    except jwt.InvalidTokenError:
        return Response({'status': 'Invalid token'}, status=401)
    


#Community Management ***** New with premium community article 
# Serializer from Community app
@api_view(['GET'])
def GetUserCommunityArticle(request, user_id):
    try:
        user = ServiceUser.objects.get(id=user_id)
    except ServiceUser.DoesNotExist:
        return Response({'status': 'user does not exist'})
    
    article = Community_Articles.objects.filter(author=user).order_by('-create_date').all()

    page = request.GET.get('page')
    paginator = Paginator(article, 10)
    
    try:
        user_article = paginator.page(page)
    except PageNotAnInteger:
        user_article = paginator.page(1)
    except EmptyPage:
        user_article = paginator.page(paginator.num_pages)

    serializer = MyPageCommunityArticleSerializer(user_article, many=True)

    return Response({
        'articles': serializer.data,
        'max_page': paginator.num_pages,
        'current_page': page
    })

@api_view(['POST'])
def DeleteUserCommunityArticle(request):
    try:
        user_id = request.data.get('user_id')
        user = ServiceUser.objects.get(id=user_id)
    except ServiceUser.DoesNotExist:
        return Response({'status': 'user does not exist'})
    
    try:
        article_id = request.data.get('article_id')
        selected_article = Community_Articles.objects.get(id=article_id)
    except Community_Articles.DoesNotExist:
        return Response({'status': 'article does not exists'})
    
    if selected_article.author == user:
        QuillContentDelete('community', selected_article.id)
        selected_article.delete()
        status = 'article_deleted'
    else:
        status = 'user does not have a permission'
    return Response({'status': status})

"""
new BM premium content for -> flutter my profile
"""

"""
Same Variable name in community views
but functions different, this variable with lower case,
returns value of authenticated users private article information
"""

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getUserProfileArticle(request):
    auth_header = request.headers.get('Authorization')
    try:
        user_id = decodeUserToken(auth_header)
        user = ServiceUser.objects.get(id=user_id)
    except ServiceUser.DoesNotExist:
        return Response({'status': 'user does not exist'})
    except jwt.ExpiredSignatureError:
        return Response({'status': 'Token expired'}, status=401)
    except jwt.InvalidTokenError:
        return Response({'status': 'Invalid token'}, status=401)
    
    """
    flutter api started spread to web
    this includes detection of page change within the myPage user profile article 
    1. my normal community article
    2. my membership community article
    3. donated article
    4. liked article (normal + membership included)
    """

    article_type = request.GET.get('type')
    
    # Serializer Calculation minimization depends on devices
    device = request.GET.get('device')
    if device == 'pc':
        is_device_pc = True
    else:
        is_device_pc = False

    if article_type == 'myArticle' or article_type == 'membership' or article_type == 'liked':
        filter_option = {}
        if article_type == 'myArticle':
            filter_option['author'] = user
        elif article_type == 'membership': #need to add model
            filter_option['author'] = user
            filter_option['is_membership'] = True
        elif article_type == 'liked':
            filter_option['likes'] = user
        article = Community_Articles.objects.filter(**filter_option).order_by('-create_date').all()

    if article_type == 'donated':
        user_donated_articles = []
        user_donation_record = Membership_Article_Donation_Record.objects.filter(donator=user)
        if user_donation_record.exists():
            for record in user_donation_record:
                user_donated_articles.append(record.article)
        article = user_donated_articles
        
    page = request.GET.get('page')
    paginator = Paginator(article, 15)
    
    try:
        user_article = paginator.page(page)
    except PageNotAnInteger:
        user_article = paginator.page(1)
    except EmptyPage:
        user_article = paginator.page(paginator.num_pages)


    serializer = MyProfileCommunityArticleSerializer(user_article, many=True, context={'is_device_pc': is_device_pc})

    return Response({
        'articles': serializer.data,
        'max_page': paginator.num_pages,
        'current_page': page
    })


# Account Cancel 

"""
For now just making false to is_active
"""

@api_view(['POST'])
def handleCancelAccount(request):
    auth_header = request.headers.get('Authorization')

    if not auth_header:
        return Response({'status' : 'not authorized'}, status=401)
    else:
        try:
            user_id = decodeUserToken(auth_header)
            user = ServiceUser.objects.get(id=user_id)
        except ServiceUser.DoesNotExist:
            return Response({'status': 'user does not exist'})
        
        except jwt.ExpiredSignatureError:
            return Response({'status': 'Token expired'}, status=401)
        
        except jwt.InvalidTokenError:
            return Response({'status': 'Invalid token'}, status=401)
        
    # survey
    try:
        cancel_reason = request.data.get('cancel_reason')
        cancel_detail = request.data.get('cancel_detail')

        survey_data = {
            'user_email': user.email,
            'title': cancel_reason,
            'detail': cancel_detail,
            'survey_type': 'Account_Cancel'
        }

        survey_form = SurveyForm(survey_data)

        if survey_form.is_valid():
            survey_form.save()
    except:
        pass

    # deactivation process ~~
    # try:
    #     user.is_active = False
    #     user.save()
    # except:
    #     return Response({'status': 'unexpected error'}, status=404)


    return Response({'status': 'account canceled'}, status=200)

    





        
    
    
