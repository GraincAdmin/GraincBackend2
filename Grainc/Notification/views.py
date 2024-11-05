from rest_framework.decorators import api_view
from rest_framework.response import Response
import jwt
from django.conf import settings
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

# Required Model
from AuthUser.models import ServiceUser, UserFCMToken
from .models import Notification

# Serializer
from .serializers import NotificationDetailSerializer, FCMTokenSerializer
# Create your views here.

#Global Function
from Grainc.Global_Function.AuthControl import decodeUserToken


    

@api_view(['GET'])
def GetNotificationDetail(request):
    auth_header = request.headers.get('Authorization')

    if auth_header:
        try:
            user_id = decodeUserToken(auth_header)
            user = ServiceUser.objects.get(id=user_id)

            type = request.GET.get('type')


            """
            Notification Model filtering with optimization
            """

            filter_condition = {
                'receivers': user
            }

            all_prefetch = [
                'notification_inquiry', 'notification_announcement',
                'notification_donation', 'notification_donation_withdrawal', 
                'notification_article', 'notification_comment', 'notification_comment_reply'
            ]

            all_related = [
                'notification_create_user', 
                'notification_comment__article', 'notification_comment__author', 
                'notification_comment_reply__reply_comment', 'notification_comment_reply__reply_comment__article', 'notification_comment_reply__author',
                'notification_donation__donator',
            ]

            if type == 'my':
                related_field = [
                    'notification_comment__article', 'notification_comment__author', 
                    'notification_comment_reply__reply_comment', 'notification_comment_reply__reply_comment__article', 'notification_comment_reply__author',
                ]
                prefetch_fields = ['notification_article', 'notification_comment', 'notification_comment_reply']
            elif type == 'service':
                related_field = ['notification_donation__donator']
                prefetch_fields = ['notification_inquiry', 'notification_announcement', 'notification_donation', 'notification_donation_withdrawal']
            else:
                related_field = all_related
                prefetch_fields = all_prefetch
                

            if type != 'all':
                if type == 'my':
                    filter_condition['notification_type__in'] = [
                        Notification.ARTICLE, 
                        Notification.COMMENT, 
                        Notification.COMMENT_REPLY
                    ]
                elif type == 'service':
                    filter_condition['notification_type__in'] = [
                        Notification.INQUIRY, 
                        Notification.ANNOUNCEMENT, 
                        Notification.DONATION, 
                        Notification.DONATION_WITHDRAWAL
                    ]

            unread_notifications = Notification.objects.filter(
                **filter_condition
            ).exclude(
                notification_on_delete=user
            ).select_related(
                *related_field
            ).prefetch_related(
                *prefetch_fields  # Unpacking the list of prefetch fields here
            ).order_by(
                '-create_date'
            ).all()

            page = request.GET.get('page')
            paginator = Paginator(unread_notifications, 4)
            
            try:
                notifications = paginator.page(page)
            except PageNotAnInteger:
                notifications = paginator.page(1)
                page = 1
            except EmptyPage:
                notifications = paginator.page(paginator.num_pages)

            # Mark notifications as read
            for notification in notifications.object_list:
                notification.notification_on_read.add(user)

            serializer = NotificationDetailSerializer(notifications, many=True)


            return Response({
                'notifications': serializer.data,
                'current_page': page,
                'max_page': paginator.num_pages,
            })

        except jwt.ExpiredSignatureError:
            return Response({'status': 'Token expired'}, status=401)
        except jwt.InvalidTokenError:
            return Response({'status': 'Invalid token'}, status=401)
    else:
        return Response({'status': 'not authorized'}, status=401)



# Notification Delete 

@api_view(['POST'])
def DeleteNotification(request):
    auth_header = request.headers.get('Authorization')

    if (auth_header):
        try:
            user_id = decodeUserToken(auth_header)
            user = ServiceUser.objects.get(id=user_id)
            
            # Notification Information
            notification_id = request.data.get('notification_id')
            selected_notification = Notification.objects.get(id=notification_id)

            selected_notification.notification_on_delete.add(user)
            selected_notification.save()
            return Response({'status': 'notification deleted'}, status=200)

        except ServiceUser.DoesNotExist:
            return Response({'status': 'User Does not exits'}, status=404)
        except jwt.ExpiredSignatureError:
            return Response({'status': 'Token expired'}, status=401)
        except jwt.InvalidTokenError:
            return Response({'status': 'Invalid token'}, status=401)
    else:
        return Response({'status': 'not authorized'}, status=401)

    

# FCM Token Register 
@api_view(['POST'])
def RegisterFCMToken(request):
    auth_header = request.headers.get('Authorization')

    if auth_header:
        try:
            user_id = decodeUserToken(auth_header)
            user = ServiceUser.objects.get(id=user_id)
        except ServiceUser.DoesNotExist:
            return Response({'status': 'User Does not exits'}, status=404)
        except jwt.ExpiredSignatureError:
            return Response({'status': 'Token expired'}, status=401)
        except jwt.InvalidTokenError:
            return Response({'status': 'Invalid token'}, status=401)
        
    else:
        return Response({'status': 'not authorized'}, status=401)
    

    token = request.data.get('token')

    if token and user:
        try:
            new_token_db = UserFCMToken.objects.create(user=user, fcm_token=token)
            return Response({'status' : 'token registered', 'token_id': new_token_db.id}, status=200)
        except:
            return Response({'status': 'token register fail'}, status=404)
        


# Notification Preference 

@api_view(['GET'])
def GetUserNotificationPreference(request):
    auth_header = request.headers.get('Authorization')

    if auth_header:
        try:
            user_id = decodeUserToken(auth_header)
            user = ServiceUser.objects.get(id=user_id)
            
        except ServiceUser.DoesNotExist:
            return Response({'status': 'User Does not exits'}, status=404)
        except jwt.ExpiredSignatureError:
            return Response({'status': 'Token expired'}, status=401)
        except jwt.InvalidTokenError:
            return Response({'status': 'Invalid token'}, status=401)
        
    else:
        return Response({'status': 'not authorized'}, status=401)
    
    token_db_id = request.GET.get('token_db_id')
    
    if token_db_id:
        try:
            token_db = UserFCMToken.objects.get(id=token_db_id, user=user)
            serializer =  FCMTokenSerializer(token_db)
            return Response(serializer.data, status=200)
        except UserFCMToken.DoesNotExist:
            return Response({'status': 'token does not exist'}, status=404)
        
    
    


# Notification Preference Change

@api_view(['POST'])
def ChangeNotificationPreference(request):
    auth_header = request.headers.get('Authorization')

    if auth_header:
        try:
            user_id = decodeUserToken(auth_header)
            user = ServiceUser.objects.get(id=user_id)
        except ServiceUser.DoesNotExist:
            return Response({'status': 'User Does not exits'}, status=404)
        except jwt.ExpiredSignatureError:
            return Response({'status': 'Token expired'}, status=401)
        except jwt.InvalidTokenError:
            return Response({'status': 'Invalid token'}, status=401)
        
    else:
        return Response({'status': 'not authorized'}, status=401)
    

    
    notification_option = request.data.get('option')

    token_db_id = request.data.get('token_db_id')

    try:
        selected_token = UserFCMToken.objects.get(id=token_db_id, user=user)
    except UserFCMToken.DoesNotExist:
        return Response({'status': 'token not found'}, status=404)
    except:
        return Response({'status': 'error'}, status=404)
    

    notification_option_types = {
        'push_notification': 'is_push_notification',

        'article': 'is_article_notification',
        'comment': 'is_comment_notification',
        'comment_reply': 'is_comment_reply_notification',

        'donation': 'is_donation_notification',
        'donation_withdrawal': 'is_donation_withdrawal_notification',

        'announcement': 'is_announcement_notification',
        'inquiry': 'is_inquiry_notification'
    }

    # Check if the provided option is valid
    if notification_option not in notification_option_types:
        return Response({'status': 'Invalid notification option'}, status=400)

    # Update the relevant notification setting by toggling its value
    option_field = notification_option_types[notification_option]
    current_value = getattr(selected_token, option_field, None)

    if current_value is not None:
        setattr(selected_token, option_field, not current_value)  # Toggle the value
        selected_token.save()  # Save the updated token

        return Response({'status': 'Notification preference updated successfully'}, status=200)
    else:
        return Response({'status': 'Invalid notification option'}, status=400)
