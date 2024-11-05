from django.utils import timezone
from dateutil.relativedelta import relativedelta
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.conf import settings
from django.contrib.humanize.templatetags.humanize import intcomma
from django.utils.html import strip_tags
from django.utils.safestring import mark_safe
# Global function
from Grainc.Global_Function.AuthControl import decodeUserToken

# DB Query 
from django.db.models import Prefetch

#login
from django.contrib.auth import authenticate
from AuthUser.serializers import MyTokenObtainPairSerializer
# Rest
import jwt
from rest_framework.decorators import api_view
from rest_framework.response import Response



"""
Models
"""
from AuthUser.models import ServiceUser
from Community.models import Community_Articles, ReportedArticlesComments, Community_Article_Comment, Community_Article_Comment_Reply
from Inquiry.models import Inquiry
from Announcement.models import Announcement
from Policy.models import CompanyPolicy, PrivacyPolicy
from Company.models import Company_Announcement
from Transaction.models import Membership_Article_Donation_Record, Membership_Donation_Withdrawal_Request
from Survey.models import Survey
from Statistics.models import CompanyRevenueStatistics

# Notification Form
from Notification.forms import NotificationForm

"""
Serializer
"""
# Inquiry
from .serializer import InquirySimpleSerializer, InquiryDetailSerializer
# User Management
from .serializer import UserManagementSerializerSimple, UserManagementSerializerDetail
# Community Management
from .serializer import AdminCommunityManagementSimple, AdminCommunityManagementDetail
# Violation
from .serializer import ReportedArticlesCommentsSimple, ReportedArticlesCommentsDetail
# Donation Record
from .serializer import DonationRecordSimple, DonationRecordDetail
# Donation Withdrawal Record
from .serializer import MembershipDonationWithdrawalRecordSimple, MembershipDonationWithdrawalRecordDetail
# Company Announcement
from .serializer import AdminCompanyAnnouncementSerializerSimple, AdminCompanyAnnouncementSerializerDetail
from .serializer import AdminCompanyPolicySerializerDetail, AdminPrivacyPolicySerializerDetail
# Company Policy
from .serializer import AdminPrivacyPolicySerializerSimple, AdminCompanyPolicySerializerSimple
# Company Announcement 
from .serializer import AdminLTDAnnouncementSerializerSimple, AdminLTDAnnouncementSerializerDetail
# Survey
from .serializer import AdminSurveySerializerSimple, AdminSurveySerializerDetail
# Statistics
from .serializer import AdminRevenueSerializer

"""
Forms
"""
# Announcement
from Announcement.forms import Announcement_Form
# Policy
from Policy.forms import SellReportsCompanyPolicy_Form, SellReportsPrivacyPolicy_Form
# Company Announcement Form
from Company.forms import Company_Announcement_Form

# Create your views here.

@api_view(['GET'])
def ServerStatusCheck(request):
    return Response({'status': 'pong'}, status=200)


@api_view(['POST'])
def AdminLogin(request):
    if request.method == 'POST':
        email = request.data.get('email')
        password = request.data.get('password')

        if email and password:
            try:
                user = authenticate(request, email=email, password=password)
            except:
                return Response(status=402)
            if user and user.is_admin:

                access_token = MyTokenObtainPairSerializer.get_token(user).access_token
                refresh_token = MyTokenObtainPairSerializer.get_token(user)
                token_data = {
                    'access': str(access_token),  # Convert AccessToken to string
                    'refresh': str(refresh_token),  # Convert RefreshToken to string
                }
                return Response({'token': token_data}, status=200)
            else:
                return Response(status=403)
        else:
            return Response(status=404)


@api_view(['GET'])
def CustomAdminDashBoard(request):
    auth_header = request.headers.get('Authorization')

    try:
        user_id = decodeUserToken(auth_header)
        user = ServiceUser.objects.get(id=user_id)
        if user.is_admin == True:
            current_date = timezone.now()
            one_month_ago = current_date - relativedelta(months=1)

            #key information field
            total_user = ServiceUser.objects.all()
            new_articles = Community_Articles.objects.filter(create_date__range=(one_month_ago, current_date)).all()

            #waiting inquiries 
            waiting_inquiry = Inquiry.objects.filter(Inquiry_reply=None).order_by('Inquiry_date').all()
            waiting_inquiry_top = waiting_inquiry[:10]

            waiting_inquiry_serializer = InquirySimpleSerializer(waiting_inquiry_top, many=True)

            return Response({
                # Statistic
                'total_user': intcomma(total_user.count()),
                'new_article': intcomma(new_articles.count()),

                # Table
                'waiting_inquiry_count': intcomma(waiting_inquiry.count()),
                'waiting_inquiry': waiting_inquiry_serializer.data
            })

        else:
            return Response({'status': 'not_admin'})
        
    except jwt.ExpiredSignatureError:
        return Response({'status': 'Token expired'}, status=401)
    except jwt.InvalidTokenError:
        return Response({'status': 'Invalid token'}, status=401)
    

# User Management
@api_view(['GET'])
def AdminUserInformationSimple(request):
    auth_header = request.headers.get('Authorization')

    try:
        user_id = decodeUserToken(auth_header)
        user = ServiceUser.objects.get(id=user_id)

        if user.is_admin == True:
            search_kw = request.GET.get('kw')
            search_filter = Q()
            if search_kw:
                search_filter = Q(email__contains=search_kw) | Q(username__contains=search_kw)


            user = ServiceUser.objects.filter(search_filter).all()
            
            page = request.GET.get('page')
            paginator = Paginator(user, 10)

            try:
                adminUsers = paginator.page(page)
            except PageNotAnInteger:
                adminUsers = paginator.page(1)
            except EmptyPage:
                adminUsers = paginator.page(paginator.num_pages)

            serializer = UserManagementSerializerSimple(adminUsers, many=True)

            return Response({
                'users': serializer.data,
                'current_page': page,
                'max_page': paginator.num_pages
            })

        else:
            return Response({'status': 'not_admin'})
        
    except jwt.ExpiredSignatureError:
        return Response({'status': 'Token expired'}, status=401)
    except jwt.InvalidTokenError:
        return Response({'status': 'Invalid token'}, status=401)
    
@api_view(['GET', 'POST'])
def AdminUserInformationDetail(request, user_id):
    auth_header = request.headers.get('Authorization')

    try:
        admin_user_id = decodeUserToken(auth_header)
        admin_user = ServiceUser.objects.get(id=admin_user_id)

        if admin_user.is_admin == True:
            selected_user = ServiceUser.objects.get(id=user_id)
            if request.method == 'POST':
                #is_active
                is_active_post = request.data.get('is_active')
                is_active = True if is_active_post else False

                #is_admin
                is_admin_post = request.data.get('is_admin')
                is_admin = True if is_admin_post else False

                selected_user.is_active = is_active
                selected_user.is_admin = is_admin

                #membership control
                is_membership_post = request.data.get('is_membership')
                is_membership = True if is_membership_post else False

                selected_user.is_membership = is_membership


                # Violation Control
                community_restriction_post = request.data.get('community_restriction')
                community_restriction = True if community_restriction_post else False

                selected_user.community_restriction = community_restriction
                selected_user.violation_detail_community = request.data.get('community_restriction_detail')

                selected_user.save()
                return Response({'status': 'user_updated'}, status=200)
            else:
                serializer = UserManagementSerializerDetail(selected_user)
                return Response(serializer.data)
        else:
            return Response({'status': 'not_admin'})

        
    except jwt.ExpiredSignatureError:
        return Response({'status': 'Token expired'}, status=401)
    except jwt.InvalidTokenError:
        return Response({'status': 'Invalid token'}, status=401)
    

# Community Management
@api_view(['GET'])
def AdminCommunitySimple(request):
    auth_header = request.headers.get('Authorization')

    try:
        user_id = decodeUserToken(auth_header)
        user = ServiceUser.objects.get(id=user_id)

        if user.is_admin == True:
            search_kw = request.GET.get('kw')
            search_filter = Q()
            if search_kw:
                search_filter = (
                    Q(author__username__contains=search_kw) | 
                    Q(author__email__contains=search_kw) | 
                    Q(subject__contains=search_kw) 
                )

            custom_filter = {

            }

            # main category
            category = request.GET.get('category')
            if category != '전체' and category :
                custom_filter['category'] = category

            sub_category = request.GET.get('sub_category')
            if sub_category != '전체' and sub_category:
                custom_filter['sub_category'] = sub_category
            
            membership = request.GET.get('membership')
            if membership != '전체' and membership:
                if membership == '멤버십':
                    custom_filter['is_membership'] = True
                else:
                    custom_filter['is_membership'] = False
            
            articles = Community_Articles.objects.prefetch_related(
                Prefetch (
                    'author',
                    queryset=ServiceUser.objects.only(
                        'username',
                        'email'
                    )
                )
            ).filter(search_filter, **custom_filter).order_by('-create_date').all()

            page = request.GET.get('page')
            paginator = Paginator(articles, 15)

            try:
                communityArticles = paginator.page(page)
            except PageNotAnInteger:
                communityArticles = paginator.page(1)
            except EmptyPage:
                communityArticles = paginator.page(paginator.num_pages)

            serializer = AdminCommunityManagementSimple(communityArticles, many=True)

            return Response({
                'articles': serializer.data,
                'current_page': page,
                'max_page': paginator.num_pages
            })

        else:
            return Response({'status': 'not_admin'})
        
    except jwt.ExpiredSignatureError:
        return Response({'status': 'Token expired'}, status=401)
    except jwt.InvalidTokenError:
        return Response({'status': 'Invalid token'}, status=401)
    
@api_view(['GET', 'POST'])
def AdminCommunityDetail(request, article_id):
    auth_header = request.headers.get('Authorization')

    try:
        user_id = decodeUserToken(auth_header)
        user = ServiceUser.objects.get(id=user_id)

        if user.is_admin == True:
            selected_article = Community_Articles.objects.prefetch_related(
                Prefetch (
                    'author',
                    queryset=ServiceUser.objects.only(
                        'username',
                    )
                )
            ).get(id = article_id)
            if request.method == 'POST':
                #is_hidden_admin
                is_hidden_admin_post = request.data.get('is_hidden_admin')
                is_hidden_admin = True if is_hidden_admin_post else False
                selected_article.is_hidden_admin = is_hidden_admin

                #is_membership
                is_membership_post = request.data.get('is_membership')
                is_membership = True if is_membership_post else False
                selected_article.is_membership = is_membership

                #is image 
                is_image_post = request.data.get('images')
                is_image = True if is_image_post else False
                selected_article.images = is_image

                #is_saved
                is_saved_post = request.data.get('is_saved')
                is_saved = True if is_saved_post else False
                selected_article.saved_article = is_saved

                selected_article.save()
                return Response({'status': 'article_updated'}, status=200)
            elif request.method == 'GET':
                serializer = AdminCommunityManagementDetail(selected_article)
            return Response(serializer.data)
        else:
            return Response({'status': 'not_admin'})
        
    except jwt.ExpiredSignatureError:
        return Response({'status': 'Token expired'}, status=401)
    except jwt.InvalidTokenError:
        return Response({'status': 'Invalid token'}, status=401)
    

@api_view(['POST'])
def AdminCommunityDelete(request, article_id):
    auth_header = request.headers.get('Authorization')

    if not auth_header:
        return Response({'status': 'not authorized'}, status=401)
    
    try:
        admin_id = decodeUserToken(auth_header)
        admin = ServiceUser.objects.get(id=admin_id)
        selected_article = Community_Articles.objects.get(id=article_id)
    except Community_Articles.DoesNotExist:
        return Response({'status': 'article not found'}, status=404)
    except ServiceUser.DoesNotExist:
        return Response({'status': 'user not found'}, status=404)
    except jwt.ExpiredSignatureError:
        return Response({'status': 'Token expired'}, status=401)
    except jwt.InvalidTokenError:
        return Response({'status': 'Invalid token'}, status=401)
    
    if not admin.is_admin:
        return Response({'status': 'not admin'})
    
    if request.method == 'POST':
        selected_article.delete()
        return Response({'status': 'article_deleted'}, status=200)
        



# Violation Report Management

@api_view(['GET'])
def AdminViolationReportSimple(request):
    auth_headers = request.headers.get('Authorization')

    if not auth_headers:
        return Response({'status': 'not authorized'}, 401)
    
    try:
        admin_id = decodeUserToken(auth_headers)
        user = ServiceUser.objects.get(id=admin_id)
    except jwt.ExpiredSignatureError:
        return Response({'status': 'Token expired'}, status=401)
    except jwt.InvalidTokenError:
        return Response({'status': 'Invalid token'}, status=401)
    
    if not user.is_admin:
        return Response({'not admin'})

    search_kw = request.GET.get('kw')
    search_filter = Q()
    if search_kw:
        search_filter = Q(reported_user__username=search_kw) | Q(type__contains=search_kw)


    custom_filter = {

    }

    violation_type = request.GET.get('violation_type')
    if violation_type != '전체' and violation_type:
        custom_filter['type'] = violation_type
    
    is_task_done = request.GET.get('is_task_done')
    if is_task_done != '전체' and is_task_done:
        if is_task_done == '처리완료':
            custom_filter['is_task_done'] = True
        else:
            custom_filter['is_task_done'] = False


    violations = ReportedArticlesComments.objects.prefetch_related(
        Prefetch (
            'reported_user',
            queryset=ServiceUser.objects.only(
                'username'
            )
        )

    ).filter(search_filter, **custom_filter).order_by('create_date')
    
    page = request.GET.get('page')
    paginator = Paginator(violations, 10)

    try:
        violationsPage = paginator.page(page)
    except PageNotAnInteger:
        violationsPage = paginator.page(1)
    except EmptyPage:
        violationsPage = paginator.page(paginator.num_pages)

    serializer = ReportedArticlesCommentsSimple(violationsPage, many=True)

    return Response({
        'violations': serializer.data,
        'current_page': page,
        'max_page': paginator.num_pages
    }, status=200)


@api_view(['GET', 'POST'])
def AdminViolationDetail(request, violation_id):
    auth_header = request.headers.get('Authorization')

    try:
        user_id = decodeUserToken(auth_header)
        user = ServiceUser.objects.get(id=user_id)

        if user.is_admin == True:

            selected_violation = ReportedArticlesComments.objects.prefetch_related(
                Prefetch (
                    'reported_user',
                    queryset=ServiceUser.objects.only(
                        'username',
                    ),
                ),
                Prefetch (
                    'reported_article__author',
                ),
                Prefetch(
                    'reported_comment__author',
                ),
                Prefetch(
                    'reported_comment_reply__author',
                )
            ).get(id=violation_id)
            if request.method == 'POST':
                # user restriction handle 
                restriction_detail = request.data.get('restriction_detail')
                
                if selected_violation.reported_article:
                    user = selected_violation.reported_article.author
                elif selected_violation.reported_comment:
                    user = selected_violation.reported_comment.author
                elif selected_violation.reported_comment_reply:
                    user = selected_violation.reported_comment_reply.author
                else:
                    return Response({'status': 'user not found'}, status=404)

                if user:
                    selected_violation.is_task_done = True
                    user.violation_detail_community = restriction_detail
                    user.community_restriction = True
                    selected_violation.save()
                    user.save()
                    return Response({'status': 'user restricted'}, status=200)

                return Response({'status': 'article_updated'}, status=200)
            elif request.method == 'GET':
                serializer = ReportedArticlesCommentsDetail(selected_violation)
            return Response(serializer.data)
        else:
            return Response({'status': 'not_admin'})
        
    except jwt.ExpiredSignatureError:
        return Response({'status': 'Token expired'}, status=401)
    except jwt.InvalidTokenError:
        return Response({'status': 'Invalid token'}, status=401)
    

@api_view(['GET'])
def getReportedContent(request, violation_id):
    auth_header = request.headers.get('Authorization')
    try:
        user_id = decodeUserToken(auth_header)
        user = ServiceUser.objects.get(id=user_id)

        if user.is_admin == True:

            selected_violation = ReportedArticlesComments.objects.prefetch_related(
                Prefetch (
                    'reported_article',
                    queryset=Community_Articles.objects.only(
                        'main_content'
                    )
                ),
                Prefetch(
                    'reported_comment',
                    queryset=Community_Article_Comment.objects.only(
                        'comment',
                    )
                ),
                Prefetch(
                    'reported_comment_reply',
                    queryset=Community_Article_Comment_Reply.objects.only(
                        'reply',
                    )
                )
            ).get(id=violation_id)
            
            content_type = request.GET.get('content_type')

            if content_type == 'article':
                return Response(mark_safe(selected_violation.reported_article.main_content))
            elif content_type == 'comment':
                return Response(selected_violation.reported_comment.comment)
            elif content_type == 'reply':
                return Response(selected_violation.reported_comment_reply.reply)

            
            serializer = ReportedArticlesCommentsDetail(selected_violation)
            return Response(serializer.data)
        else:
            return Response({'status': 'not_admin'})
        
    except jwt.ExpiredSignatureError:
        return Response({'status': 'Token expired'}, status=401)
    except jwt.InvalidTokenError:
        return Response({'status': 'Invalid token'}, status=401)



# donation
    

@api_view(['GET'])
def AdminDonationRecordSimple(request):
    auth_header = request.headers.get('Authorization')

    if not auth_header:
        return Response({'status': 'not authorized'}, status=401)
    
    try:
        admin_id = decodeUserToken(auth_header)
        admin = ServiceUser.objects.get(id=admin_id)
    except jwt.ExpiredSignatureError:
        return Response({'status': 'Token expired'}, status=401)
    except jwt.InvalidTokenError:
        return Response({'status': 'Invalid token'}, status=401)
    
    if not admin.is_admin:
        return Response({'status': 'not admin'})
    

    search_kw = request.GET.get('kw')
    search_filter = Q()
    if search_kw:
        search_filter = Q(donator__username__contains=search_kw) | Q(article__subject__contains=search_kw)


    records = Membership_Article_Donation_Record.objects.prefetch_related(
        Prefetch (
            'article',
            queryset=Community_Articles.objects.only(
                'subject'
            )
        ),
        Prefetch(
            'donator',
            queryset=ServiceUser.objects.only(
                'username'
            )
        ),
    ).filter(search_filter).order_by('-donation_date')
    
    page = request.GET.get('page')
    paginator = Paginator(records, 10)

    try:
        donationRecord = paginator.page(page)
    except PageNotAnInteger:
        donationRecord = paginator.page(1)
    except EmptyPage:
        donationRecord = paginator.page(paginator.num_pages)

    serializer = DonationRecordSimple(donationRecord, many=True)

    return Response({
        'donations': serializer.data,
        'current_page': page,
        'max_page': paginator.num_pages
    }, status=200)

@api_view(['GET', 'POST'])
def AdminDonationRecordDetail(request, donation_id):
    auth_header = request.headers.get('Authorization')

    try:
        user_id = decodeUserToken(auth_header)
        user = ServiceUser.objects.get(id=user_id)

        if user.is_admin == True:
            records = Membership_Article_Donation_Record.objects.select_related(
                'article',  # Fetch the article in the same query
                'donator'   # Fetch the donator in the same query
            ).prefetch_related(
                Prefetch(
                    'article__author',
                    queryset=ServiceUser.objects.only('username')
                )
            ).only(
                'article__subject',  # Get only the subject field from Community_Articles
                'donator__username'   # Get only the username from the donator
            ).get(id=donation_id)


            if request.method == 'POST':

                return Response({'status': 'article_updated'}, status=200)
            elif request.method == 'GET':
                serializer = DonationRecordDetail(records)
            return Response(serializer.data)
        else:
            return Response({'status': 'not_admin'})
        
    except jwt.ExpiredSignatureError:
        return Response({'status': 'Token expired'}, status=401)
    except jwt.InvalidTokenError:
        return Response({'status': 'Invalid token'}, status=401)
    

# Donation Withdrawal Record

@api_view(['GET'])
def AdminDonationWithdrawalRecordSimple(request):
    auth_header = request.headers.get('Authorization')

    if not auth_header:
        return Response({'status': 'not authorized'}, status=401)
    
    try:
        admin_id = decodeUserToken(auth_header)
        admin = ServiceUser.objects.get(id=admin_id)
    except jwt.ExpiredSignatureError:
        return Response({'status': 'Token expired'}, status=401)
    except jwt.InvalidTokenError:
        return Response({'status': 'Invalid token'}, status=401)
    
    if not admin.is_admin:
        return Response({'status': 'not admin'})
    

    search_kw = request.GET.get('kw')
    search_filter = Q()
    if search_kw:
        search_filter = (
            Q(request_user__email__contains=search_kw) | 
            Q(request_user__username__contains=search_kw) |
            Q(account_holder__icontains=search_kw) |
            Q(bank_account__icontains=search_kw) 
        )   

    custom_filter = {

    }

    task_status = request.GET.get('task_status')
    if task_status != '전체' and task_status:
        custom_filter['status'] = task_status


    records = Membership_Donation_Withdrawal_Request.objects.select_related(
        'request_user'
    ).only('request_user__username').filter(search_filter, **custom_filter).order_by('request_date')

    
    page = request.GET.get('page')
    paginator = Paginator(records, 10)

    try:
        withdrawalRecord = paginator.page(page)
    except PageNotAnInteger:
        withdrawalRecord = paginator.page(1)
    except EmptyPage:
        withdrawalRecord = paginator.page(paginator.num_pages)

    serializer = MembershipDonationWithdrawalRecordSimple(withdrawalRecord, many=True)

    return Response({
        'donation_withdrawal_record': serializer.data,
        'current_page': page,
        'max_page': paginator.num_pages
    }, status=200)


@api_view(['GET', 'POST'])
def AdminDonationWithdrawalRecordDetail(request, withdrawal_record_id):
    auth_header = request.headers.get('Authorization')

    try:
        user_id = decodeUserToken(auth_header)
        user = ServiceUser.objects.get(id=user_id)

        if user.is_admin == True:
            records = Membership_Donation_Withdrawal_Request.objects.select_related(
                'request_user'
            ).only('request_user__username').get(id=withdrawal_record_id)


            if request.method == 'POST':
                
                updated_status = request.data.get('status')

                try: 
                    records.status = updated_status
                    if updated_status == 'failed':
                        rejection_message_post = request.data.get('rejection_message')
                        records.rejection_message = rejection_message_post
                        
                    records.save()
                except:
                    return Response({'status': 'failed to update'}, status=404)


                return Response({'status': 'article_updated'}, status=200)
            elif request.method == 'GET':
                serializer = MembershipDonationWithdrawalRecordDetail(records)
            return Response(serializer.data)
        else:
            return Response({'status': 'not_admin'})
        
    except jwt.ExpiredSignatureError:
        return Response({'status': 'Token expired'}, status=401)
    except jwt.InvalidTokenError:
        return Response({'status': 'Invalid token'}, status=401)


# Inquiry Management

@api_view(['GET'])
def AdminInquiryManagement(request):
    auth_header = request.headers.get('Authorization')

    try:
        user_id = decodeUserToken(auth_header)
        user = ServiceUser.objects.get(id=user_id)

        if user.is_admin == True:
            search_kw = request.GET.get('kw')
            search_filter = Q()
            if search_kw:
                search_filter = (
                    Q(User__username__icontains=search_kw) | 
                    Q(User__email__icontains=search_kw) | 
                    Q(Inquiry_type__icontains=search_kw) | 
                    Q(Inquiry_subject__icontains=search_kw)
                )

            custom_filter = {
            }

            is_task_completed = request.GET.get('task_status')
            
            if is_task_completed:
                if is_task_completed == '미답변':
                    answer_type = False
                    custom_filter['is_replied'] = answer_type
                else:
                    answer_type = True
                    custom_filter['is_replied'] = answer_type

            
            inquiry_type = request.GET.get('inquiry_type')

            if inquiry_type and inquiry_type != '전체':
                custom_filter['Inquiry_type'] = inquiry_type
            

            
            inquiry = Inquiry.objects.filter(search_filter, **custom_filter).select_related(
                'User'
            ).only('User__username').order_by('Inquiry_date').all()

            page = request.GET.get('page')
            paginator = Paginator(inquiry, 10)

            try:
                adminInquiry = paginator.page(page)
            except PageNotAnInteger:
                adminInquiry = paginator.page(1)
            except EmptyPage:
                adminInquiry = paginator.page(paginator.num_pages)

            serializer = InquirySimpleSerializer(adminInquiry, many=True)

            return Response({
                'inquiry': serializer.data,
                'current_page': page,
                'max_page': paginator.num_pages
            })

        else:
            return Response({'status': 'not_admin'})
        
    except jwt.ExpiredSignatureError:
        return Response({'status': 'Token expired'}, status=401)
    except jwt.InvalidTokenError:
        return Response({'status': 'Invalid token'}, status=401)
    
@api_view(['GET', 'POST'])
def InquiryManagementDetail(request, inquiry_id):
    auth_header = request.headers.get('Authorization')

    try:
        user_id = decodeUserToken(auth_header)
        user = ServiceUser.objects.get(id=user_id)

        if user.is_admin == True:
            selected_inquiry = Inquiry.objects.select_related(
                'User'
            ).only('User__username').get(id=inquiry_id)
            if request.method == 'POST':
                inquiry_reply = request.data.get('reply')
                reply_date = timezone.now()
                selected_inquiry.Inquiry_reply_date = reply_date
                selected_inquiry.Inquiry_reply = inquiry_reply
                if inquiry_reply:
                    selected_inquiry.is_replied = True
                else:
                    selected_inquiry.is_replied = False
                selected_inquiry.save()
                return Response({'status': 'report_updated'}, status=200)
            else:
                serializer = InquiryDetailSerializer(selected_inquiry)
            return Response(serializer.data)
        else:
            return Response({'status': 'not_admin'})
        
    except jwt.ExpiredSignatureError:
        return Response({'status': 'Token expired'}, status=401)
    except jwt.InvalidTokenError:
        return Response({'status': 'Invalid token'}, status=401)



# Company Announcement 

@api_view(['GET'])
def AdminCompanyAnnouncementManagement(request):
    auth_header = request.headers.get('Authorization')

    try:
        user_id = decodeUserToken(auth_header)
        user = ServiceUser.objects.get(id=user_id)

        if user.is_admin == True:
            search_kw = request.GET.get('kw')
            search_filter = Q()
            if search_kw:
                search_filter = Q(subject__contains=search_kw)

            
            announcements = Announcement.objects.filter(search_filter).order_by('-create_date').all()

            page = request.GET.get('page')
            paginator = Paginator(announcements, 10)

            try:
                adminAnnouncements = paginator.page(page)
            except PageNotAnInteger:
                adminAnnouncements = paginator.page(1)
            except EmptyPage:
                adminAnnouncements = paginator.page(paginator.num_pages)

            serializer = AdminCompanyAnnouncementSerializerSimple(adminAnnouncements, many=True)

            
            return Response({
                'announcement': serializer.data,
                'current_page': page,
                'max_page': paginator.num_pages
            })

        else:
            return Response({'status': 'not_admin'})
        
    except jwt.ExpiredSignatureError:
        return Response({'status': 'Token expired'}, status=401)
    except jwt.InvalidTokenError:
        return Response({'status': 'Invalid token'}, status=401)
    


@api_view(['GET', 'POST'])
def AdminAnnouncementDetail(request, announcement_id):
    auth_header = request.headers.get('Authorization')

    try:
        user_id = decodeUserToken(auth_header)
        user = ServiceUser.objects.get(id=user_id)

        if user.is_admin == True:
            selected_announcement = Announcement.objects.get(id=announcement_id)
            if request.method == 'POST':
                announcement_subject = request.data.get("subject")
                announcement_content = request.data.get('content')
                is_important_post = request.data.get('is_important')
                is_important = True if is_important_post else False
                start_time = request.data.get('start_time')
                end_time = request.data.get('end_time')
                
                selected_announcement.subject = announcement_subject
                selected_announcement.content = announcement_content
                selected_announcement.is_important = is_important
                selected_announcement.start_time = start_time
                selected_announcement.end_time = end_time


                selected_announcement.save()
                return Response({'status': 'announcement_updated'}, status=200)
            else:
                serializer = AdminCompanyAnnouncementSerializerDetail(selected_announcement)
                return Response(serializer.data)
                
        else:
            return Response({'status': 'not_admin'})


    except jwt.ExpiredSignatureError:
        return Response({'status': 'Token expired'}, status=401)
    except jwt.InvalidTokenError:
        return Response({'status': 'Invalid token'}, status=401)
    

# Announcement Notification Count Live Update

@api_view(['POST'])
def AdminNewAnnouncement(request):
    auth_header = request.headers.get('Authorization')

    try:
        user_id = decodeUserToken(auth_header)
        user = ServiceUser.objects.get(id=user_id)

        if user.is_admin:
            new_announcement_data = {
                'create_date': timezone.now(),
                'subject': request.data.get('subject'),
                'content': request.data.get('content'),
                'is_important': request.data.get('is_important'),
                'start_time': request.data.get('start_time'),
                'end_time': request.data.get('end_time'),
            }
            announcement_creation_form = Announcement_Form(new_announcement_data)

            if announcement_creation_form.is_valid():
                new_announcement = announcement_creation_form.save()

                # Notification Creation
                notification_receivers = ServiceUser.objects.all()

                notification_data = {
                    'notification_type': 'announcement',
                    'notification_create_user': user,
                    'receivers': notification_receivers,
                    'notification_announcement': new_announcement
                }

                notification_form = NotificationForm(notification_data)

                if notification_form.is_valid():
                    notification_form.save()
                

                else:
                    print(notification_form.errors)

                return Response({'status': 'new_announcement_created'})
            else:
                return Response({'errors': announcement_creation_form.errors}, status=400)
        else:
            return Response({'status': 'not_admin'}, status=403)
    except jwt.ExpiredSignatureError:
        return Response({'status': 'Token expired'}, status=401)
    except jwt.InvalidTokenError:
        return Response({'status': 'Invalid token'}, status=401)
    except ServiceUser.DoesNotExist:
        return Response({'status': 'user_not_found'}, status=404)


# Company Policy
@api_view(['GET'])
def AdminCompanyPolicy(request):
    auth_header = request.headers.get('Authorization')

    try:
        user_id = decodeUserToken(auth_header)
        user = ServiceUser.objects.get(id=user_id)

        if user.is_admin == True:
            search_kw = request.GET.get('kw')
            search_filter = Q()
            if search_kw:
                search_filter = Q(policy_content__contains=search_kw) 

            policy_type = request.GET.get('type')

            if policy_type == 'company':
                policy = CompanyPolicy.objects.filter(search_filter).order_by('-create_date').all()
            else:
                policy = PrivacyPolicy.objects.filter(search_filter).order_by('-create_date').all()
                
            page = request.GET.get('page')
            paginator = Paginator(policy, 10)

            try:
                adminPolicy = paginator.page(page)
            except PageNotAnInteger:
                adminPolicy = paginator.page(1)
            except EmptyPage:
                adminPolicy = paginator.page(paginator.num_pages)

            if policy_type == 'company':
                serializer = AdminCompanyPolicySerializerSimple(adminPolicy, many=True)
            else:
                serializer = AdminPrivacyPolicySerializerSimple(adminPolicy, many=True)
            
            return Response({
                'policy': serializer.data,
                'current_page': page,
                'max_page': paginator.num_pages
            })

        else:
            return Response({'status': 'not_admin'})
        
    except jwt.ExpiredSignatureError:
        return Response({'status': 'Token expired'}, status=401)
    except jwt.InvalidTokenError:
        return Response({'status': 'Invalid token'}, status=401)
    

@api_view(['GET', 'POST'])
def AdminPolicyDetail(request,  policy_type, policy_id):
    auth_header = request.headers.get('Authorization')

    try:
        user_id = decodeUserToken(auth_header)
        user = ServiceUser.objects.get(id=user_id)
        if user.is_admin == True:
            if policy_type == 'company':
                policy = CompanyPolicy.objects.get(id=policy_id)
                serializer = AdminCompanyPolicySerializerDetail(policy)
            elif policy_type == 'privacy':
                policy = PrivacyPolicy.objects.get(id=policy_id)
                serializer = AdminPrivacyPolicySerializerDetail(policy)

            if request.method == 'POST':
                policy.policy_content = request.data.get('policyContent')
                policy.save()
                return Response({'status': 'policy_modified'}, status=200)
            else:
                if policy_type == 'company':
                    serializer = AdminCompanyPolicySerializerDetail(policy)
                elif policy_type == 'privacy':
                    serializer = AdminPrivacyPolicySerializerDetail(policy)
                return Response(serializer.data)

        else:
            return Response({'status': 'not_admin'})

    except jwt.ExpiredSignatureError:
        return Response({'status': 'Token expired'}, status=401)
    except jwt.InvalidTokenError:
        return Response({'status': 'Invalid token'}, status=401)
    
@api_view(['POST'])
def AdminNewPolicy(request, policy_type):
    auth_header = request.headers.get('Authorization')

    try:
        user_id = decodeUserToken(auth_header)
        user = ServiceUser.objects.get(id=user_id)

        if user.is_admin == True:
            new_policy_data = {
                'create_date': timezone.now(),
                'policy_content': request.data.get('policyContent')
            }
            if policy_type == 'new_company_policy':
                form = SellReportsCompanyPolicy_Form(new_policy_data)
            elif policy_type == 'new_privacy_policy':
                form = SellReportsPrivacyPolicy_Form(new_policy_data)

            if form.is_valid():
                form.save()
                return Response({'status': 'new_policy_uploaded'}, status=200)
            else:
                return Response({'status': form.errors}, status=403)

        else:
            return Response({'status': 'not_admin'})

    except jwt.ExpiredSignatureError:
        return Response({'status': 'Token expired'}, status=401)
    except jwt.InvalidTokenError:
        return Response({'status': 'Invalid token'}, status=401)
    
@api_view(['POST'])
def AdminPolicyDelete(request, policy_type,  policy_id):
    auth_header = request.headers.get('Authorization')
    
    if not auth_header:
        return Response({'status': 'not authorized'}, status=401)
    
    try:
        admin_id = decodeUserToken(auth_header)
        admin = ServiceUser.objects.get(id=admin_id)

        if policy_type == 'company':
            policy = CompanyPolicy.objects.get(id=policy_id)
        else:
            policy = PrivacyPolicy.objects.get(id=policy_id)
        
    except CompanyPolicy.DoesNotExist:
        return Response({'status': 'policy does not exist'}, status=404) 
    except PrivacyPolicy.DoesNotExist:
        return Response({'status': 'policy does not exist'}, status=404)            
    except jwt.ExpiredSignatureError:
        return Response({'status': 'Token expired'}, status=401)
    except jwt.InvalidTokenError:
        return Response({'status': 'Invalid token'}, status=401)
    
    if not admin.is_admin:
        return Response({'status': 'not admin'})
    
    policy.delete()

    return Response({'status': 'policy deleted'}, status=200)
    

# Company Announcement

@api_view(['GET'])
def AdminLTDAnnouncement(request):
    auth_header = request.headers.get('Authorization')

    try:
        user_id = decodeUserToken(auth_header)
        user = ServiceUser.objects.get(id=user_id)

        if user.is_admin == True:
            search_kw = request.GET.get('kw')
            search_filter = Q()
            if search_kw:
                search_filter = Q(Company_Announcement_Subject__contains=search_kw) 

            company_announcement = Company_Announcement.objects.filter(search_filter).order_by('-Company_Announcement_Date')
            
            page = request.GET.get('page')
            paginator = Paginator(company_announcement, 10)

            try:
                adminCompanyAnnouncement = paginator.page(page)
            except PageNotAnInteger:
                adminCompanyAnnouncement = paginator.page(1)
            except EmptyPage:
                adminCompanyAnnouncement = paginator.page(paginator.num_pages)

            serializer = AdminLTDAnnouncementSerializerSimple(adminCompanyAnnouncement, many=True)
            
            return Response({
                'company_announcement': serializer.data,
                'current_page': page,
                'max_page': paginator.num_pages
            })

        else:
            return Response({'status': 'not_admin'})
        
    except jwt.ExpiredSignatureError:
        return Response({'status': 'Token expired'}, status=401)
    except jwt.InvalidTokenError:
        return Response({'status': 'Invalid token'}, status=401)
    

@api_view(['GET', 'POST'])
def AdminLTDAnnouncementDetail(request, announcement_id):
    auth_header = request.headers.get('Authorization')

    try:
        user_id = decodeUserToken(auth_header)
        user = ServiceUser.objects.get(id=user_id)
        if user.is_admin == True:
            selected_company_announcement = Company_Announcement.objects.get(id=announcement_id)
            if request.method == "POST":
                announcement_content = request.data.get('Company_Announcement_Content')
                announcement_subject = request.data.get('Company_Announcement_Subject')
                selected_company_announcement.Company_Announcement_Content = announcement_content
                selected_company_announcement.Company_Announcement_Subject = announcement_subject
                selected_company_announcement.save()
                return Response({'status': 'company_announcement_modified'}, status=200)
            else:
                serializer = AdminLTDAnnouncementSerializerDetail(selected_company_announcement)
                return Response(serializer.data)
        else:
            return Response({'status': 'not_admin'})
        
    except jwt.ExpiredSignatureError:
        return Response({'status': 'Token expired'}, status=401)
    except jwt.InvalidTokenError:
        return Response({'status': 'Invalid token'}, status=401)
    

@api_view(['POST'])
def AdminNewLTDAnnouncement(request):
    auth_header = request.headers.get('Authorization')

    try:
        user_id = decodeUserToken(auth_header)
        user = ServiceUser.objects.get(id=user_id)
        if user.is_admin == True:
            if request.method == "POST":
                new_company_announcement_data = {
                    'Company_Announcement_Content': request.data.get('Company_Announcement_Content'),
                    'Company_Announcement_Subject': request.data.get('Company_Announcement_Subject'),
                    'Company_Announcement_Date': timezone.now()
                }
                form = Company_Announcement_Form(new_company_announcement_data)
                
                if form.is_valid():
                    form.save()
                    return Response({'status': 'new_company_announcement_uploaded'}, status=200)
                else:
                    return Response({'status': form.errors}, status=403)

        else:
            return Response({'status': 'not_admin'})

    except jwt.ExpiredSignatureError:
        return Response({'status': 'Token expired'}, status=401)
    except jwt.InvalidTokenError:
        return Response({'status': 'Invalid token'}, status=401)
    

@api_view(['POST'])
def AdminLTDAnnouncementDelete(request,  announcement_id):
    auth_header = request.headers.get('Authorization')
    
    if not auth_header:
        return Response({'status': 'not authorized'}, status=401)
    
    try:
        admin_id = decodeUserToken(auth_header)
        admin = ServiceUser.objects.get(id=admin_id)
        announcement = Company_Announcement.objects.get(id=announcement_id)
        
    except Company_Announcement.DoesNotExist:
        return Response({'status': 'announcement does not exist'}, status=404)            
    except jwt.ExpiredSignatureError:
        return Response({'status': 'Token expired'}, status=401)
    except jwt.InvalidTokenError:
        return Response({'status': 'Invalid token'}, status=401)
    
    if not admin.is_admin:
        return Response({'status': 'not admin'})
    
    announcement.delete()

    return Response({'status': 'announcement deleted'}, status=200)



@api_view(['GET'])
def AdminSurvey(request):
    auth_header = request.headers.get('Authorization')

    try:
        user_id = decodeUserToken(auth_header)
        user = ServiceUser.objects.get(id=user_id)

        if user.is_admin == True:
            survey_type_get = request.GET.get('type')

            custom_search_filter = {
                
            }

            if survey_type_get != '전체':
                if survey_type_get == '회원탈퇴':
                    custom_search_filter['survey_type'] = 'account_cancel'

            survey = Survey.objects.filter(**custom_search_filter).order_by('-create_date')
            
            page = request.GET.get('page')
            paginator = Paginator(survey, 10)

            try:
                adminSurvey = paginator.page(page)
            except PageNotAnInteger:
                adminSurvey = paginator.page(1)
            except EmptyPage:
                adminSurvey = paginator.page(paginator.num_pages)

            serializer = AdminSurveySerializerSimple(adminSurvey, many=True)
            
            return Response({
                'survey': serializer.data,
                'current_page': page,
                'max_page': paginator.num_pages
            })

        else:
            return Response({'status': 'not_admin'})
        
    except jwt.ExpiredSignatureError:
        return Response({'status': 'Token expired'}, status=401)
    except jwt.InvalidTokenError:
        return Response({'status': 'Invalid token'}, status=401)
    


@api_view(['GET'])
def AdminSurveyDetail(request, survey_id):
    auth_header = request.headers.get('Authorization')

    try:
        user_id = decodeUserToken(auth_header)
        user = ServiceUser.objects.get(id=user_id)
        if user.is_admin == True:
            selected_survey = Survey.objects.get(id=survey_id)

            serializer = AdminSurveySerializerDetail(selected_survey)
            return Response(serializer.data)
        else:
            return Response({'status': 'not_admin'})
        
    except jwt.ExpiredSignatureError:
        return Response({'status': 'Token expired'}, status=401)
    except jwt.InvalidTokenError:
        return Response({'status': 'Invalid token'}, status=401)
    


"""
PO performance measure
"""

@api_view(['GET'])
def AdminGetRevenueData(request):
    auth_header = request.headers.get('Authorization')
    
    if not auth_header:
        return Response({'status': 'not authorized'}, status=401)
    
    try:
        admin_id = decodeUserToken(auth_header)
        admin = ServiceUser.objects.get(id=admin_id)        
    except jwt.ExpiredSignatureError:
        return Response({'status': 'Token expired'}, status=401)
    except jwt.InvalidTokenError:
        return Response({'status': 'Invalid token'}, status=401)
    
    if not admin.is_admin:
        return Response({'status': 'not admin'})
    
    # revenue data
    
    # test just get first data 

    revenue_data = CompanyRevenueStatistics.objects.order_by('-create_date').first()
    serializer = AdminRevenueSerializer(revenue_data)

    return Response(serializer.data)
