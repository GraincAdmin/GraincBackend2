from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db import transaction
from django.db.models import Q
from .models import Community_Articles
from .serializers import CommunityArticleSerializers, CommunityArticleSerializersSimple, MyProfileCommunityArticleSerializer
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils import timezone
from datetime import timedelta
from django.contrib.humanize.templatetags.humanize import intcomma
import jwt

# DB Query 
from django.db.models import Prefetch

# Global Function
from Grainc.Global_Function.SensitiveInformationFilter import sensitive_content_filtering
from Grainc.Global_Function.ContentDataFormatter import create_date_formatter
from Grainc.Global_Function.ImgProcessorQuill import QuillImageProcessor, QuillImageProcessorModification, extract_img_urls, RandomFolderName
from Grainc.Global_Function.AuthControl import decodeUserToken, getUserInformation
from Notification.tasks import CreateNewNotification

#Community Bookmark
from .models import CommunityBookmarkFolder, CommunityBookmark
from AuthUser.models import ServiceUser
from .serializers import CommunityBookmarkFolderSerializer
from .forms import CommunityBookmarkForm, CommunityBookmarkFolderForm

#Membership 
from Transaction.models import Membership_Article_Donation_Record
from Transaction.forms import MembershipDonationRecordFrom
from .models import Community_Membership_Article_Free_Trial
#Community Comment
from .models import Community_Article_Comment, Community_Article_Comment_Reply
from .forms import CommunityCommentForm, CommunityCommentReplyForm
from .serializers import CommunityCommentsSerializer, CommunityCommentReplySerializer

#Community Article Upload
from .forms import CommunityArticleForm
# Community Article Modification + Saved Article
from .serializers import UploadedArticleSerializer, UserSavedArticleStatusSerializer

# Article Reporting
from .forms import ReportedArticlesCommentsForm
from .models import ReportedArticlesComments


# Create your views here.


"""
DB Query Optimization (select_related, prefetch_related)
"""

# Community Article Serializer Query

CommunityArticleSerializerSR = [
    'author'
]

CommunityArticleSerializerPR = [
    Prefetch('author',
        queryset=ServiceUser.objects.only(
            'id', 
            'username', 
            'profile_image', 
            'introduction'
        )
    )
]

# Community Comments Serializer Query

CommunityCommentsSerializerSR = [
    'author',
]

CommunityCommentsSerializerPR = [
    Prefetch(
        'author',
        queryset=ServiceUser.objects.only(
            'id',
            'username',
            'profile_image'
        )
    )
]

# Community Comments Reply Serializer Query 

CommunityCommentReplySerializerSR = [
    'author'
]

CommunityCommentReplySerializerPR = [
    Prefetch(
        'author',
        queryset=ServiceUser.objects.only(
            'id',
            'username',
            'profile_image'
        )
    )
]




"""
community main views
"""

@api_view(['GET'])
def HomeCommunityArticleMostLiked(request):
    try:
        one_month_ago = timezone.now() - timedelta(days=30)
        articles = Community_Articles.objects.filter(
            saved_article=False, 
            images=True,
            create_date__gte=one_month_ago,
            is_hidden_admin = False
        ).select_related(
            *CommunityArticleSerializerSR
        ).prefetch_related(
            *CommunityArticleSerializerPR
        ).exclude(
            likes=None
        ).order_by(
            '-likes', 
            '-create_date'
        )[:3]
        
        user = getUserInformation(request)
        if isinstance(user, Response):
            return user
        
        serializer = CommunityArticleSerializers(articles, many=True, context={'user': False})
        return Response(serializer.data)
    except Exception as e:
        print(e)
        return Response({'error': str(e)}, status=500)
    
"""
For Application ios, android
community home
"""
@api_view(['GET'])
def HomeCommunityArticleLatest(request):
    selected_article = request.GET.get('category')
    try:
        one_month_ago = timezone.now() - timedelta(days=30)
        most_liked_articles = Community_Articles.objects.filter(
            saved_article=False, 
            images=True,
            create_date__gte=one_month_ago
        ).select_related(
            *CommunityArticleSerializerSR
        ).prefetch_related(
            *CommunityArticleSerializerPR
        ).exclude(
            likes=None
        ).order_by(
            '-likes', 
            '-create_date'
        )[:3]

        articles = Community_Articles.objects.filter(
            saved_article=False, is_hidden_admin = False, category = selected_article
        ).select_related(
            *CommunityArticleSerializerSR
        ).prefetch_related(
            *CommunityArticleSerializerPR
        ).exclude(id__in=most_liked_articles.values_list('id')).order_by('-likes', '-create_date')[:3]

        user = getUserInformation(request)
        if isinstance(user, Response):
            return user
            
        serializer = CommunityArticleSerializers(articles, many=True, context={'user': user})
        return Response(serializer.data)
    except Exception as e:
        return Response({'error': str(e)}, status=500)


# Global View Function


@api_view(['GET'])
def get_community_article(request, article_id):
    try:
        # Fetch the article by its ID
        article = Community_Articles.objects.select_related(
            *CommunityArticleSerializerSR
        ).prefetch_related(
            *CommunityArticleSerializerPR
        ).get(id=article_id)
    except Community_Articles.DoesNotExist:
        return Response({'status': 'article does not exist'}, status=404)
    
        
    # membership control
    user = getUserInformation(request)
    if isinstance(user, Response):
        return user
        
    if article.is_membership and article.author != user:
        article_primary_data = {
            'id': article.id,
            'is_membership': True,
            'subject': article.subject,
            'category': article.category,
            'sub_category': article.sub_category,
            'main_content': '',
            'create_date': create_date_formatter(article.create_date),
            'views': intcomma(article.views),
            'comments_count': intcomma(article.comments),
            'likes_count': intcomma(article.likes.count()),
            'likes': [{'id': like.id} for like in article.likes.all()],  # 직렬화
            'views_validation': [{'id': view.id} for view in article.views_validation.all()],
            'author_id': article.author.id,
            'author_username': article.author.username,
            'author_profile_image': article.author.profile_image.url,
            'is_bookmarked': False,

        }
        if user:
            if not user.is_membership:
                today = timezone.now().date()
                has_viewed_article_today = Community_Membership_Article_Free_Trial.objects.filter(
                user=user, view_date=today, article=article).exists()

                if has_viewed_article_today:
                    pass
                elif not has_viewed_article_today:
                    return Response({
                        'article': article_primary_data,
                        'free_trial_request': True,
                    }, status=200)
            else:
                pass
        else:
            # login required
            return Response({'article': article_primary_data}, status=200)

    serializer = CommunityArticleSerializers(article, context={'user': user, 'is_user_data': True})
    return Response({'article': serializer.data})



@api_view(['GET', 'POST'])
def articleFreeTrial(request):
    auth_header = request.headers.get('Authorization')
    
    if auth_header:
        try:
            user_id = decodeUserToken(auth_header)
            user = ServiceUser.objects.get(id=user_id)

            article_id = request.GET.get('article_id')
            article = Community_Articles.objects.get(id=article_id)
        except ServiceUser.DoesNotExist:
            return Response({'status': 'user does not exist'}, status=404)
        except Community_Articles.DoesNotExist:
            return Response({'status': 'article does not exist'}, status=404)
        except jwt.ExpiredSignatureError:
            return Response({'status': 'Token expired'}, status=401)
        except jwt.InvalidTokenError:
            return Response({'status': 'Invalid token'}, status=401)
        
        if not user.is_membership:
            today = timezone.now().date()
            views_today = Community_Membership_Article_Free_Trial.objects.filter(user=user, view_date=today).count()

            # Handle POST request to register the free trial
            if request.method == 'POST':
                if views_today >= 1:
                    return Response({
                        'free_trial_limit': True,
                        'free_trial_count': 0,
                    }, status=403)  # Status 403 to indicate trial limit exceeded

                # Register the free trial view
                free_trial_entry = Community_Membership_Article_Free_Trial(user=user, article=article)
                free_trial_entry.save()
                free_trial_count = 10 - (views_today + 1)  # Account for the new view
                return Response({
                    'free_trial_limit': False,
                    'free_trial_count': free_trial_count,
                }, status=200)
        else:
            return Response({
                'free_trial_limit': False,
                'free_trial_count': None,
            }, status=200)
    else:
        return Response({'status': 'not authorized'}, status=401)
    

@api_view(['POST'])
def community_article_view_update(request, article_id):
    auth_header = request.headers.get('Authorization')
    if auth_header:
        try:
            user_id = decodeUserToken(auth_header)
            user = ServiceUser.objects.get(id=user_id)
            selected_article = Community_Articles.objects.get(id=article_id)

            if user in selected_article.views_validation.all():
                status = 'viewed'
            else:
                selected_article.views += 1
                selected_article.views_validation.add(user)
                selected_article.save()
                status = 'added'

            return Response({'status': status}, status=200)
        except Community_Articles.DoesNotExist:
            return Response({'status': 'article does not exits'}) 
        
        except ServiceUser.DoesNotExist:
            return Response({'status': 'user does not exits'})
        
        except jwt.ExpiredSignatureError:
            return Response({'status': 'Token expired'}, status=401)
        
        except jwt.InvalidTokenError:
            return Response({'status': 'Invalid token'}, status=401)
    

"""
Started from Mobile API and Expanded to Web
"""
@api_view(['GET'])
def MainCommunityArticle(request):
    category = request.GET.get('category')
    sub_category = request.GET.get('sub_category')
    order_by = request.GET.get('order_by')
    content_type = request.GET.get('content_type')

    filter_conditions = {
        'is_hidden_admin': False,
        'category': category,
    }

    if content_type == 'community':
        filter_conditions['is_membership'] = False
    elif content_type == 'membership':
        filter_conditions['is_membership'] = True

    if sub_category != "전체":
        filter_conditions['sub_category'] = sub_category

        
    if order_by == "최신순":
        selected_order_by = '-create_date'
    if order_by == "인기순":
        selected_order_by = 'likes'
    if order_by == "조회순":
        selected_order_by = '-views'


    # main_community_articles = (
    #     Community_Articles.objects
    #     .filter(**filter_conditions)
    #     .order_by(selected_order_by)
    #     .select_related('author')  # Use select_related for FK relationships
    #     .prefetch_related('likes', 'comments')  # Use prefetch_related for many-to-many relationships
    # )


    main_community_articles = Community_Articles.objects.filter(
        **filter_conditions
        ).select_related(
            *CommunityArticleSerializerSR
        ).prefetch_related(
            *CommunityArticleSerializerPR
        ).order_by(selected_order_by).all()

    page = request.GET.get('page')
    paginator = Paginator(main_community_articles, 15)

    try:
        articles = paginator.page(page)
    except PageNotAnInteger:
        articles = paginator.page(1)
    except EmptyPage:
        articles = paginator.page(paginator.num_pages)

    # user prob to pass serializer 
    auth_headers = request.headers.get('Authorization')
    user = None
    if auth_headers:
        try:
            user_id = decodeUserToken(auth_headers)
            user = ServiceUser.objects.get(id=user_id)

        except ServiceUser.DoesNotExist:
            return Response({'status': 'user does not exits'})
        
        except jwt.ExpiredSignatureError:
            return Response({'status': 'Token expired'}, status=401)
        
        except jwt.InvalidTokenError:
            return Response({'status': 'Invalid token'}, status=401)

    serializer = CommunityArticleSerializers(articles, many=True)

    return Response({
        'articles': serializer.data,
        'max_page': paginator.num_pages,  # This gives you the maximum page number
        'current_page': page
    })


@api_view(['GET'])
def AuthorsArticle(request, current_article_id):
    try:
        current_article = Community_Articles.objects.get(id=current_article_id)
        author = current_article.author
        other_article = Community_Articles.objects.filter(author=author).exclude(id=current_article_id)[:3]
        serializer = CommunityArticleSerializersSimple(other_article, many=True)
        return Response(serializer.data)
    except Community_Articles.DoesNotExist:
        return Response({'status': 'article does not exists'})


@api_view(['GET'])
def ArticleRecommendation(request, current_article_id):
    try:
        current_article = Community_Articles.objects.select_related(
            *CommunityArticleSerializerSR
        ).prefetch_related(
            *CommunityArticleSerializerPR
        ).get(id=current_article_id)

        recommendation = Community_Articles.objects.select_related(
            *CommunityArticleSerializerSR
        ).prefetch_related(
            *CommunityArticleSerializerPR
        ).exclude(id=current_article_id).filter(images=True, category=current_article.category)[:5]
        serializer = CommunityArticleSerializers(recommendation, many=True)
        return Response(serializer.data)
    except Community_Articles.DoesNotExist:
        return Response({'status': 'article does not exists'})
#Bookmark System

"""
Flutter Start User Bookmark get
"""
@api_view(['GET'])
def BookmarkFolder(request):
    auth_headers = request.headers.get('Authorization')
    if auth_headers :
        try: 
            user_id = decodeUserToken(auth_headers)
            user = ServiceUser.objects.get(id=user_id)

            user_bookmark_folder = CommunityBookmarkFolder.objects.filter(folder_owner=user).order_by('-create_date').all()

            page = request.GET.get('page')
            paginator = Paginator(user_bookmark_folder, 10)

            try:
                folders = paginator.page(page)
            except PageNotAnInteger:
                folders = paginator.page(1)
            except EmptyPage:
                folders = paginator.page(paginator.num_pages)

            serializer = CommunityBookmarkFolderSerializer(folders, many=True)
            
            return Response({
                'folders': serializer.data,
                'current_page': page,
                'max_page': paginator.num_pages
            })
            
        except ServiceUser.DoesNotExist:
            return Response({'status': 'user does not exits'})
        
        except jwt.ExpiredSignatureError:
            return Response({'status': 'Token expired'}, status=401)
        
        except jwt.InvalidTokenError:
            return Response({'status': 'Invalid token'}, status=401)
        
    else:
        return Response({'status': 'not authorized'}, status=401)




@api_view(['GET'])
def BookmarkStatusCheck(request, user_id, article_id):
    try:
        user = ServiceUser.objects.get(id=user_id)
        selected_article = Community_Articles.objects.get(id=article_id)
    except ServiceUser.DoesNotExist:
        return Response({'status': 'user-does-not-exist'}, status=404)
    except Community_Articles.DoesNotExist:
        return Response({'status': 'article-does-not-exist'}, status=404)
        
    user_bookmark_folder = CommunityBookmarkFolder.objects.filter(folder_owner=user, bookmarks=selected_article).all()
    if user_bookmark_folder.exists():
        bookmark_status = True
    else:
        bookmark_status = False

    return Response({'bookmark_status' : bookmark_status}, status=200)

    
@api_view(['POST'])
@transaction.atomic
def CommunityBookmarkAdd(request, article_id, folder_id, user_id):
    try:
        user = ServiceUser.objects.get(id=user_id)
    except ServiceUser.DoesNotExist:
        return Response({'status': 'user identification failed'}, status=404)
    
    try:
        selected_folder = CommunityBookmarkFolder.objects.get(id=folder_id)
        if selected_folder.folder_owner != user:
            return Response({'status': 'folder_owner_not_match'}, status=403)
    except CommunityBookmarkFolder.DoesNotExist:
        return Response({'status': 'folder_does_not_exist'}, status=404)
    
    try:
        selected_article = Community_Articles.objects.get(id=article_id)
    except Community_Articles.DoesNotExist:
        return Response({'status': 'article_not_found'}, status=404)
    
    if request.method == 'POST':
        if selected_article in selected_folder.bookmarks.all():
            selected_folder.bookmarks.remove(selected_article)
            CommunityBookmark.objects.filter(bookmark_folder=selected_folder, bookmark_article=selected_article).delete()
            selected_folder.save()
            status = "bookmark_removed"
        else:
            bookmark_add_data = {
                'bookmark_folder': selected_folder,
                'bookmark_article': selected_article
            }
            form = CommunityBookmarkForm(bookmark_add_data)
            if form.is_valid():
                selected_folder.bookmarks.add(selected_article)
                form.save()
                selected_folder.save()
                status = "bookmark_saved"
            else:
                return Response({'status': 'form_invalid', 'errors': form.errors}, status=400)
    
    return Response({'status': status})
    
@api_view(['POST'])
def CommunityBookmarkFolderAdd(request):
    auth_header = request.headers.get('Authorization')
    if (auth_header):
        if request.method == "POST":
            try:
                user_id = decodeUserToken(auth_header)
                user = ServiceUser.objects.get(id=user_id)
            except ServiceUser.DoesNotExist:
                return Response({'status': 'user does not exits'})
            except jwt.ExpiredSignatureError:
                return Response({'status': 'Token expired'}, status=401)
            except jwt.InvalidTokenError:
                return Response({'status': 'Invalid token'}, status=401)
            
            #new folder variable
            folderName = request.data.get('folder_name')

            #user folder check
            is_folder_name_not_unique = CommunityBookmarkFolder.objects.filter(folder_owner= user, folder_name=folderName).exists()

            if is_folder_name_not_unique:
                return Response({'status': 'folder_exists'}, status=409)
            else:
                new_folder_data = {
                    'folder_name': folderName,
                    'folder_owner': user
                }
                form = CommunityBookmarkFolderForm(new_folder_data)

                if form.is_valid():
                    new_folder = form.save()
                    status = "folder_created"
                    return Response({
                        'status': status, 
                        'folder_id': new_folder.id,
                        'folder_name': folderName}, status=200)
                else:
                    status = form.errors
                    return Response({'status': status}, status=404)
    else:
        return Response({'status': 'not authorized'}, status=401)
        
@api_view(['POST'])
def CommunityBookmarkFolderNameEdit(request):
    auth_header = request.headers.get('Authorization')
    if (auth_header):
        try:
            user_id = decodeUserToken(auth_header)
            user = ServiceUser.objects.get(id=user_id)
            
            folder_id = request.data.get('folder_id')
            selected_folder = CommunityBookmarkFolder.objects.get(id=folder_id)
            
            if user == selected_folder.folder_owner:
                new_folder_name = request.data.get('new_folder_name')
                if CommunityBookmarkFolder.objects.filter(folder_owner=user, folder_name=new_folder_name).exists():
                    return Response({'status': 'folder_name_exists'}, status=409)
                else:
                    selected_folder.folder_name = new_folder_name
                    selected_folder.save()
                    return Response({'status': 'folder name changed'}, status=200)
            else:
                return Response({'status': 'not authorized'}, status=404)


        except ServiceUser.DoesNotExist:
            return Response({'status': 'user does not exits'})
        except CommunityBookmarkFolder.DoesNotExist:
            return Response({'status': 'folder does not exits'})
        except jwt.ExpiredSignatureError:
            return Response({'status': 'Token expired'}, status=401)
        except jwt.InvalidTokenError:
            return Response({'status': 'Invalid token'}, status=401)
        
    else:
        return Response({'status': 'nto authorized'}, status=401)


#Community Like Button

@api_view(['GET'])
def CommunityLikeStatus(request, user_id, article_id):
    try:
        user = ServiceUser.objects.get(id=user_id)
    except:
        return Response({'status': 'user_not_found'})

    selected_article = Community_Articles.objects.get(id=article_id)

    if user in selected_article.likes.all():
        status = 'liked'
    else:
        status = "disliked"
    return Response({'status': status})



@api_view(['POST'])
def CommunityLike(request, user_id, article_id):
    try:
        user = ServiceUser.objects.get(id=user_id)
    except ServiceUser.DoesNotExist:
        return Response({'status': 'user identification failed'})

    try:
        selected_article = Community_Articles.objects.get(id=article_id)
        author = selected_article.author
    except Community_Articles.DoesNotExist:
        return Response({'status': 'article identification failed'})

    if request.method == "POST":
        if user in selected_article.likes.all():
            selected_article.likes.remove(user)
            status = 'disliked'
            if author:
                author.likes_count -= 1
        else:
            selected_article.likes.add(user)
            if author:
                author.likes_count += 1
            status = 'liked'
        selected_article.save()
        if author:
            author.save()
        like_count = selected_article.likes.count()
    else:
        return Response({'status': 'invalid request method'})

    return Response({'status': status, 'like_count': like_count})



from Grainc.Global_Variable.MembershipPrice import donation_per_click
@api_view(['POST'])
def MembershipDonation(request):
    auth_header = request.headers.get('Authorization')
    if (auth_header):
        try:
            donating_user_id = decodeUserToken(auth_header)
            donating_user = ServiceUser.objects.get(id=donating_user_id)

            selected_article_id = request.data.get('article_id')
            selected_article = Community_Articles.objects.get(id=selected_article_id)

        except ServiceUser.DoesNotExist:
            return Response({'status': 'user does not exist'}, status=404)
        except Community_Articles.DoesNotExist:
            return Response({'status': 'article does not exist'}, status=404)
        except jwt.ExpiredSignatureError:
            return Response({'status': 'Token expired'}, status=401)
        except jwt.InvalidTokenError:
            return Response({'status': 'Invalid token'}, status=401)
        

        # user membership verification
        if donating_user.is_membership and selected_article.is_membership:
            if donating_user != selected_article.author:
                # check did user donated to author today
                today = timezone.now().date()

                # Filter donations made today
                donator_todays_donation_record = Membership_Article_Donation_Record.objects.filter(
                    donator=donating_user,
                    donation_date__date=today  # Filters by the date part of donation_date
                )

                # check user daily donation limit (current 5 times)
                if donator_todays_donation_record.count() < 5:
                    # Check if the user has already donated to the author today
                    if donator_todays_donation_record.filter(article__author=selected_article.author).exists():
                        return Response({'status': '오늘 후원한 유저입니다'}, status=403)
                    else:
                        donation_amount = donation_per_click #very important fix based on company policy changes
                        # Donation Process
                        donation_detail = {
                            'article': selected_article,
                            'donator': donating_user,
                            'amount': donation_amount,
                        }
                        donation_form = MembershipDonationRecordFrom(donation_detail)

                        if donation_form.is_valid():
                            selected_article.author.membership_donation_cash += donation_amount
                            donation = donation_form.save()
                            CreateNewNotification('donation', donation)

                            if selected_article.author.donation_message:
                                donation_message = selected_article.author.donation_message
                            else:
                                donation_message = '후원완료'

                            return Response({'status': donation_message}, status=200)
                        else:
                            return Response({'status': '후원중 문제가 생겼습니다'}, status=404)
                else:
                    return Response({'status': '일일 후원 한도에 도달했습니다 5/5'}, status=403)
                
            else:
                return Response({'status': '자신의 글에는 후원이 불가합니다'}, status=403)
        else:
            return Response({'status': '후원은 멤버십 유저만 가능합니다'}, status=403)
    else:
        return Response({'status': 'not authorized'}, status=401)

#comment

@api_view(['GET'])
def CommunityArticleComments(request, article_id, page_section):
    try:
        selected_article = Community_Articles.objects.get(id=article_id)
    except:
        return Response({'status': 'article request error'}, status=404)
    try:
        if page_section == "article":
            article_comments = Community_Article_Comment.objects.select_related(
                    *CommunityCommentsSerializerSR
                ).prefetch_related(
                    *CommunityCommentsSerializerPR
                ).filter(
                    article=selected_article
                ).order_by(
                    '-create_date'
                )[:2]
        else:
            comments = Community_Article_Comment.objects.select_related(
                    *CommunityArticleSerializerSR
                ).prefetch_related(
                    *CommunityArticleSerializerPR
                ).filter(article=selected_article).order_by('-create_date').all()
            
            page = request.GET.get('page')
            paginator = Paginator(comments, 10)
            article_comments = paginator.get_page(page)   
    except:
        return Response({'status': 'comment request error'}, status=404)
    
    serializer = CommunityCommentsSerializer(article_comments, many=True)
    
    if page_section == "article":
        return Response({'comments': serializer.data})
    else:
        return Response({
            'comments': serializer.data,
            'max_page': paginator.num_pages,  # This gives you the maximum page number
            'current_page': page
        })


@api_view(['POST'])
def CommunityCommentUpload(request, article_id):
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return Response({'status': 'not authorized'}, status=401)
    try:
        user_id = decodeUserToken(auth_header)
        user = ServiceUser.objects.get(id=user_id)
    except ServiceUser.DoesNotExist:
        return Response({'status': 'user identification failed'}, status=404)
    except jwt.ExpiredSignatureError:
        return Response({'status': 'Token expired'}, status=401)
    except jwt.InvalidTokenError:
        return Response({'status': 'Invalid token'}, status=401)
    
    try:
        selected_article = Community_Articles.objects.get(id=article_id)
    except Community_Articles.DoesNotExist:
        return Response({'status': 'article not found'}, status=404)
    
    if request.method == "POST":
        if not user.community_restriction:
            comment_data = request.data.get('comment')
            comment_data = {
                'author': user,
                'article': selected_article,
                'comment': sensitive_content_filtering(comment_data)
            }

            form = CommunityCommentForm(comment_data)

            if form.is_valid():
                comment = form.save() 
                selected_article.comments += 1
                selected_article.save()
                status = 'comment_submitted'
                CreateNewNotification('comment', comment)
            else:
                return Response({'status': 'form_invalid', 'errors': form.errors}, status=400)
        else:
            return Response({
                'restriction' : user.community_restriction,
                'restriction_detail': user.violation_detail_community
            })

    return Response({'status': status, 'comment_id': comment.id}) # Flutter update for live update

@api_view(['POST'])
def CommunityCommentDelete(request):
    auth_header = request.headers.get('Authorization')

    try:
        user_id = decodeUserToken(auth_header)
        user = ServiceUser.objects.get(id=user_id)

        comment_id = request.data.get('comment_id')
        selected_comment = Community_Article_Comment.objects.get(id=comment_id)
        selected_article = selected_comment.article
        if user == selected_comment.author:
            selected_article.comments -= 1
            selected_article.save()
            selected_comment.delete()
            return Response({'status': 'comment_deleted'}, status=200)
        else:
            return Response({'status': 'comment_deleted_failed'}, status=403)

    except Community_Article_Comment.DoesNotExist:
        return Response({'status': 'comment does not exits'})

    except ServiceUser.DoesNotExist:
        return Response({'status': 'user does not exits'})
    
    except jwt.ExpiredSignatureError:
        return Response({'status': 'Token expired'}, status=401)
    
    except jwt.InvalidTokenError:
        return Response({'status': 'Invalid token'}, status=401)
    
@api_view(['POST'])
def CommunityCommentLike(request, comment_id):
    auth_header = request.headers.get('Authorization')

    if (auth_header):
        try:
            user_id = decodeUserToken(auth_header)
            user = ServiceUser.objects.get(id=user_id)

            comment = Community_Article_Comment.objects.get(id=comment_id)
            if user in comment.comment_likes.all():
                comment.comment_likes.remove(user)
                status = 'liked'
            else:
                comment.comment_likes.add(user)
                status = 'disliked'
            
            comment.save()

            return Response({'status' : status}, status=200)

        except ServiceUser.DoesNotExist:
            return Response({'status': 'user does not exist'}, status=404)
        except Community_Article_Comment.DoesNotExist:
            return Response({'status': 'comment does not exist'}, status=404)
        except jwt.ExpiredSignatureError:
            return Response({'status': 'Token expired'}, status=401)
        except jwt.InvalidTokenError:
            return Response({'status': 'Invalid token'}, status=401)
    else:
        return Response({'status': 'unauthorized'}, status=401)
    
@api_view(['GET'])
def CommunityCommentLikeCount(request, comment_id):
    try:
        selected_comment = Community_Article_Comment.objects.get(id=comment_id)
        comment_count = intcomma(selected_comment.comment_likes.count())

        # let default value for unauthenticated 
        user_liked = False

        auth_header = request.headers.get('Authorization')
        if auth_header:
            try:
                user_id = decodeUserToken(auth_header)
                user = ServiceUser.objects.get(id=user_id)
                
                if user in selected_comment.comment_likes.all():
                    user_liked = True
                else:
                    user_liked = False
            except ServiceUser.DoesNotExist:
                pass
            
        return Response({
            'like_count': intcomma(comment_count),
            'user_liked': user_liked
        }, status=200)

    except Community_Article_Comment.DoesNotExist:
        return Response({'status': 'comment does not exists'}, status=404)
    


@api_view(['GET'])
def CommunityCommentReplyView(request, comment_id):


    try:
        comment_reply = Community_Article_Comment_Reply.objects.select_related(
            *CommunityCommentReplySerializerSR
        ).prefetch_related(
            *CommunityCommentReplySerializerPR
        ).filter(reply_comment = comment_id).order_by('-create_date')
    except Community_Article_Comment_Reply.DoesNotExist:
        return Response({'status': 'comment reply not found'}, status=404)
    

    page = request.GET.get('page')
    paginator = Paginator(comment_reply, 15)

    try:
        reply = paginator.page(page)
    except PageNotAnInteger:
        reply = paginator.page(1)
    except EmptyPage:
        reply = paginator.page(paginator.num_pages)
    
    serializer = CommunityCommentReplySerializer(reply, many=True)
        
    return Response ({
        'reply': serializer.data,
        'current_page': page,
        'max_page': paginator.num_pages
    }, status=200)


@api_view(['POST']) 
def CommunityCommentReply(request, comment_id):
    auth_header = request.headers.get('Authorization')
    try:
        user_id = decodeUserToken(auth_header)
        user = ServiceUser.objects.get(id=user_id)
    except ServiceUser.DoesNotExist:
        return Response({'status': 'user identification failed'}, status=404)
    
    try:
        selected_comment = Community_Article_Comment.objects.get(id=comment_id)
    except Community_Article_Comment.DoesNotExist:
        return Response({'status': 'comment not found'}, status=404)
    
    if request.method == 'POST':
        if not user.community_restriction:
            reply_data = request.data.get('reply')
            comment_reply_data = {
                'author': user,
                'reply_comment': selected_comment,
                'reply': sensitive_content_filtering(reply_data)
            }

            form = CommunityCommentReplyForm(comment_reply_data)

            if form.is_valid():
                reply = form.save()
                selected_comment.reply_count += 1
                selected_comment.save()

                if user != selected_comment.author:
                    CreateNewNotification('comment_reply', reply)   

                return Response({'status': 'reply submitted', 'reply_id': reply.id})
            else:
                Response({'status': form.error}, status=404)

            return Response({'status': 'comment reply submitted'})
        else:
            return Response({
                'restriction': user.community_restriction,
                'restriction_detail': user.violation_detail_community,
            })


@api_view(['POST'])
def CommunityCommentReplyDelete(request):
    auth_header = request.headers.get('Authorization')
    if auth_header:
        try:
            user_id = decodeUserToken(auth_header)
            user = ServiceUser.objects.get(id=user_id)

            reply_id = request.data.get('reply_id') 
            selected_reply = Community_Article_Comment_Reply.objects.get(id=reply_id)
            target_comment = selected_reply.reply_comment

            if user == selected_reply.author:
                target_comment.reply_count -= 1
                target_comment.save()
                selected_reply.delete()
                return Response({'status': 'reply_deleted'}, status=200)
            else:
                return Response({'status': 'bad_request'}, status=403)
            
        except Community_Article_Comment_Reply.DoesNotExist:
            return Response({'status': 'reply does not exits'}, status=404)
        
        except ServiceUser.DoesNotExist:
            return Response({'status': 'user does not exits'})
        
        except jwt.ExpiredSignatureError:
            return Response({'status': 'Token expired'}, status=401)
        
        except jwt.InvalidTokenError:
            return Response({'status': 'Invalid token'}, status=401)
    else:
        return Response({'status', 'not authorized'}, status=401)
    
@api_view(['POST'])
def CommunityCommentModification(request):
    auth_header = request.headers.get('Authorization')
    if auth_header:
        try:
            user_id = decodeUserToken(auth_header)
            user = ServiceUser.objects.get(id=user_id)
        except ServiceUser.DoesNotExist:
            return Response({'status': 'user does not exits'})
        
        except jwt.ExpiredSignatureError:
            return Response({'status': 'Token expired'}, status=401)
        
        except jwt.InvalidTokenError:
            return Response({'status': 'Invalid token'}, status=401)
        
        comment_type = request.data.get('type')
        comment_id = request.data.get('comment_id')
        modified_comment = request.data.get('modified_comment')

        if comment_type == 'comment':
            selected_comment = Community_Article_Comment.objects.get(id=comment_id)
        elif comment_type == 'reply':
            selected_comment = Community_Article_Comment_Reply.objects.get(id=comment_id)

        if user == selected_comment.author:
            if comment_type == 'comment':
                selected_comment.comment = sensitive_content_filtering(modified_comment)
            elif comment_type == 'reply':
                selected_comment.reply = sensitive_content_filtering(modified_comment)
            selected_comment.save()
            return Response({'status', 'comment modified'}, status=200)
        else:
            return Response({'status', 'not authorized'}, status=404)

    return Response({'status': 'Not Authorized'}, status=401)
 
    
@api_view(['GET'])
def GetCommunityCommentPageDetail(request, article_id):
    try:
        selected_article = Community_Articles.objects.get(id=article_id)
    except:
        return Response({'status': 'article request error'}, status=404)
    
    return Response({
        'create_date': selected_article.create_date.strftime('%Y.%m.%d:%H.%M'),
        'subject': selected_article.subject,
        'comment_count': selected_article.comments
    })

#article upload + user violation check
@api_view(['POST', 'GET'])
def article_upload(request):
    auth_header = request.headers.get('Authorization')
    if (auth_header):
        try:
            user_id = decodeUserToken(auth_header)
            user = ServiceUser.objects.get(id=user_id)
        except ServiceUser.DoesNotExist:
            return Response({'status': 'user does not exits'})
        
        except jwt.ExpiredSignatureError:
            return Response({'status': 'Token expired'}, status=401)
        
        except jwt.InvalidTokenError:
            return Response({'status': 'Invalid token'}, status=401)
    else:
        return Response({'status': 'not authorized'}, status=401)

    """
    Community User Violation Check
    """
    if request.method == 'GET':
        return Response ({
            'restriction': user.community_restriction, 
            'violation_detail': user.violation_detail_community,
            'is_membership': user.is_membership
        })

    """
    Community Article Upload and Modification
    """
    if request.method == "POST":
        if user.community_restriction == False:
            upload_type = request.data.get('upload_type')

            # Extract data from request
            subject = request.data.get('subject')
            category = request.data.get('category')
            sub_category = request.data.get('sub_category')
            hashtags = request.data.get('hashtags')
            main_content = request.data.get('main_content')
            content_type = request.data.get('content_type')

            # membership check 
            if user.is_membership:
                if content_type == 'membership':
                    is_membership_content =  True
                else:
                    is_membership_content = False
            else:
                is_membership_content = False

            if upload_type == 'new' or upload_type == 'save':
                if upload_type == 'new':
                    saved_article = False
                elif upload_type == 'save':
                    saved_article = True

                # for new content
                S3_folder_path = RandomFolderName()
                updated_main_content = QuillImageProcessor('community', main_content, S3_folder_path, user.pk)

                if extract_img_urls(updated_main_content):
                    images = True
                else:
                    images = False

                new_article_data = {
                    'author': user,
                    'subject': sensitive_content_filtering(subject),
                    'category': category,
                    'sub_category': sub_category,
                    'hashtags': hashtags,
                    'is_membership' : is_membership_content,
                    'main_content': sensitive_content_filtering(updated_main_content),
                    'images': images,
                    'saved_article': saved_article,
                    'unique_folder_name': S3_folder_path
                }

                form = CommunityArticleForm(new_article_data)

                if form.is_valid():
                    user.article_count += 1
                    article = form.save()
                    user.save()
                    status = '커뮤니티글 업로드 완료'
                    if upload_type == 'new':
                        CreateNewNotification('article', article)
                else:
                    status = form.errors
                return Response({'status': status, 'article_id': article.id}, status=200)

            elif upload_type == 'modification':
                try:
                    article_id = request.data.get('article_id')
                    selected_article = Community_Articles.objects.get(id=article_id)
                except Community_Articles.DoesNotExist:
                    return Response({'status': 'article_does_not_exist'})
                
                """ 
                Modification Process
                """
                
                if user == selected_article.author:
                    # Process image changes and update content
                    updated_main_content = QuillImageProcessorModification(
                        'community',
                        selected_article.main_content,
                        main_content,
                        selected_article.unique_folder_name,
                        selected_article.author.pk
                    )

                    if extract_img_urls(updated_main_content):
                        images = True
                    else:
                        images = False

                    # Update article fields
                    selected_article.category = category
                    selected_article.sub_category = sub_category
                    selected_article.hashtags = hashtags
                    selected_article.subject = sensitive_content_filtering(subject)
                    selected_article.is_membership = is_membership_content  # Fixed here
                    selected_article.main_content = sensitive_content_filtering(updated_main_content)
                    selected_article.images = images
                    selected_article.save()
                    return Response({'status': 'article modified', 'article_id': selected_article.id}, status=200)
                else:
                    return Response({'status': 'not authorized'}, status=403)
        else:
            return Response ({
                'restriction': user.community_restriction, 
                'violation_detail': user.violation_detail_community
            })


@api_view(['GET'])
def GetModifyingArticleData(request, article_id):
    try:
        selected_article = Community_Articles.objects.get(id=article_id)
    except Community_Articles.DoesNotExist:
        return Response({'status': 'article_does_not_exits'})

    serializer = UploadedArticleSerializer(selected_article)

    return Response(serializer.data)

@api_view(['GET'])
def GetUserSavedArticle(request):
    auth_header = request.headers.get('Authorization')
    try:
        user_id = decodeUserToken(auth_header)
        user = ServiceUser.objects.get(id=user_id)
        
        user_saved_articles = Community_Articles.objects.filter(author=user, saved_article=True).order_by('-create_date')

        page = request.GET.get('page')
        paginator = Paginator(user_saved_articles, 6)
        try:
            user_article = paginator.page(page)
        except PageNotAnInteger:
            user_article = paginator.page(1)
        except EmptyPage:
            user_article = paginator.page(paginator.num_pages)

        serializer = UserSavedArticleStatusSerializer(user_article, many=True)

        return Response({
            'saved_articles': serializer.data,
            'current_page': page,
            'max_page': paginator.num_pages
        })

    except ServiceUser.DoesNotExist:
        return Response({'status': 'user does not exist'})
    
    except jwt.ExpiredSignatureError:
        return Response({'status': 'Token expired'}, status=401)
    
    except jwt.InvalidTokenError:
        return Response({'status': 'Invalid token'}, status=401)
    
@api_view(['GET'])
def LoadUserSavedArticle(request, article_id):
    auth_header = request.headers.get('Authorization')
    try:
        user_id = decodeUserToken(auth_header)
        user = ServiceUser.objects.get(id=user_id)
        
        selected_saved_articles = Community_Articles.objects.get(id=article_id)

        if user == selected_saved_articles.author:
            serializer = UploadedArticleSerializer(selected_saved_articles)
            return Response(serializer.data)
        else:
            return Response({'status': 'not authorized'}, status=304)

    except ServiceUser.DoesNotExist:
        return Response({'status': 'user does not exist'})
    
    except jwt.ExpiredSignatureError:
        return Response({'status': 'Token expired'}, status=401)
    
    except jwt.InvalidTokenError:
        return Response({'status': 'Invalid token'}, status=401)
    
@api_view(['POST'])
def DeleteUserSavedArticle(request, article_id):
    auth_header = request.headers.get('Authorization')
    try:
        user_id = decodeUserToken(auth_header)
        user = ServiceUser.objects.get(id=user_id)
        
        selected_saved_articles = Community_Articles.objects.get(id=article_id)

        if user == selected_saved_articles.author:
            selected_saved_articles.delete()
            user.article_count -= 1
            user.save()
            return Response({'status': 'saved_article_delete'}, status=200)
        else:
            return Response({'status': 'not authorized'}, status=304)

    except ServiceUser.DoesNotExist:
        return Response({'status': 'user does not exist'})
    
    except jwt.ExpiredSignatureError:
        return Response({'status': 'Token expired'}, status=401)
    
    except jwt.InvalidTokenError:
        return Response({'status': 'Invalid token'}, status=401)

# User Profile
"""
Flutter Start API User Profile
shared variable name in AuthUser, but in different return 
it shows only globally opened information, which excludes donated article
"""

@api_view(['GET'])
def GetUserProfileArticle(request, user_id):
    try:
        user = ServiceUser.objects.get(id=user_id)
    except:
        return Response({'status': 'user not identified'})
    
    type = request.GET.get('type')

    # Serializer Calculation minimization depends on devices
    device = request.GET.get('device')
    if device == 'pc':
        is_device_pc = True
    else:
        is_device_pc = False

    filter_options = {}

    if type == 'community':
        filter_options['author'] = user
    elif type == 'membership':
        filter_options['author'] = user
        filter_options['is_membership'] = True
    elif type == 'liked':
        filter_options['likes'] = user
    
    community_article = Community_Articles.objects.filter(**filter_options).order_by('-create_date')
    

    page = request.GET.get('page')
    paginator = Paginator(community_article, 15)
    try:
        user_article = paginator.page(page)
    except PageNotAnInteger:
        user_article = paginator.page(1)
    except EmptyPage:
        user_article = paginator.page(paginator.num_pages)
    num_page = paginator.num_pages
        

    serializer = MyProfileCommunityArticleSerializer(user_article, many=True, context={'is_device_pc': is_device_pc})
    return Response({
        'articles': serializer.data,
        'max_page': num_page, # This gives you the maximum page number
        'current_page': page
    })



"""
Get Searched Article For Flutter and PC (migrated)
"""

@api_view(['GET'])
def GetSearchedArticle(request):
    search_kw = request.GET.get('kw')
    search_filter = Q()
    if search_kw:
        search_filter = (
            Q(subject__contains=search_kw) | 
            Q(main_content__contains=search_kw) | 
            Q(category=search_kw) | 
            Q(sub_category=search_kw) | 
            Q(hashtags__contains=search_kw) | 
            Q(author__username__contains=search_kw)
        )


    filter_conditions = {
        'is_hidden_admin': False,
    }

    sub_category = request.GET.get('sub_category')
    if sub_category != '전체':
        filter_conditions['sub_category'] = sub_category


    content_type = request.GET.get('content_type')

    if content_type == 'community':
        filter_conditions['is_membership'] = False
    elif content_type == 'membership':
        filter_conditions['is_membership'] = True


    order_by = request.GET.get('order_by')
    if order_by == "최신순":
        selected_order_by = '-create_date'
    if order_by == "인기순":
        selected_order_by = 'likes'
    if order_by == "조회순":
        selected_order_by = '-views'

    
    articles = Community_Articles.objects.filter(
        search_filter, 
        **filter_conditions
        ).select_related(
            *CommunityArticleSerializerSR
        ).prefetch_related(
            *CommunityArticleSerializerPR
        ).order_by(selected_order_by).all()

    page = request.GET.get('page')
    paginator = Paginator(articles, 15)
    try:
        searched_articles = paginator.page(page)
    except PageNotAnInteger:
        searched_articles = paginator.page(1)
    except EmptyPage:
        searched_articles = paginator.page(paginator.num_pages)

    auth_header = request.headers.get('Authorization')
    user = None
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

    article_serializer = CommunityArticleSerializers(searched_articles, many=True, context={'user': user})

    return Response({
        'articles': article_serializer.data,
        'current_page': page,
        'max_page': paginator.num_pages,
        'results_count': intcomma(articles.count())
    })

#bookmark
@api_view(['GET'])
def GetBookmarkedArticles(request):
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
        

        folder_id = request.GET.get('folder')

        try:
            article_bookmark = CommunityBookmarkFolder.objects.get(id=folder_id)
        except CommunityBookmarkFolder.DoesNotExist:
            return Response({'folder_does_not_exist'}, status=404)

        if user != article_bookmark.folder_owner:
            return Response({'status': 'not folder owner'})

        bookmarks_list = list(
            article_bookmark.bookmarks.select_related(
                *CommunityArticleSerializerSR
            ).prefetch_related(
                *CommunityArticleSerializerPR
            ).all()
        )  # Convert to list
        page = request.GET.get('page', 1)  # Set default value to 1

        paginator = Paginator(bookmarks_list, 15)  # Paginate bookmarks list

        try:
            bookmark_articles = paginator.page(page)
        except PageNotAnInteger:
            bookmark_articles = paginator.page(1)
        except EmptyPage:
            bookmark_articles = paginator.page(paginator.num_pages)


        user = getUserInformation(request)
        if isinstance(user, Response):
            return user

        serializer = CommunityArticleSerializers(bookmark_articles, many=True, context={'user': user})

        return Response({
            'article': serializer.data,
            'bookmark_count': intcomma(article_bookmark.bookmarks.count()),
            'folder_name': article_bookmark.folder_name,
            'max_page': paginator.num_pages,
            'current_page': bookmark_articles.number
        })
    else:
        return Response({'status': 'not authorized'}, status=401)

@api_view(['POST'])
def DeleteCommunityBookmarkFolder(request):
    auth_header = request.headers.get('Authorization')
    if (auth_header):
        if request.method == 'POST':
            try:
                user_id = decodeUserToken(auth_header)
                user = ServiceUser.objects.get(id=user_id)
            except ServiceUser.DoesNotExist:
                return Response({'status': 'user does not exist'})

            try:
                folder_id = request.data.get('folder_id')
                bookmark_folder = CommunityBookmarkFolder.objects.get(id=folder_id)
            except CommunityBookmarkFolder.DoesNotExist:
                return Response({'status': 'folder does not exits'})
            
            if user != bookmark_folder.folder_owner:
                return Response({'status': 'user is not folder owner'})
            elif user == bookmark_folder.folder_owner:
                bookmark_folder.delete()
                return Response({'status': 'folder_removed'})
    else:
        return Response({'status': 'not authorized'}, status=401)
        


# Article Reporting Management

@api_view(['POST'])
def CreateArticleReport(request):   
    auth_header = request.headers.get('Authorization')
    if auth_header:
        if request.method == 'POST':
            try:
                user_id = decodeUserToken(auth_header)
                user = ServiceUser.objects.get(id=user_id)

            except ServiceUser.DoesNotExist:
                return Response({'status': 'user does not exists'}, status=404)
            except jwt.ExpiredSignatureError:
                return Response({'status': 'Token expired'}, status=401)
            
            except jwt.InvalidTokenError:
                return Response({'status': 'Invalid token'}, status=401)


            reporting_id = request.data.get('reporting_id')
            reporting_content_type = request.data.get('reporting_content_type')
            reporting_category = request.data.get('reporting_category')
            reporting_detail = request.data.get('reporting_detail')

            reporting_data = {
                'type': reporting_category,
                'detail': reporting_detail
            }
            if reporting_content_type == 'article':
                try:
                    selected_article = Community_Articles.objects.get(id=reporting_id)
                    reporting_data['reported_article'] = selected_article

                    reporting_qualification = ReportedArticlesComments.objects.filter(
                        reported_user=user, 
                        reported_article=selected_article
                    )
                    if reporting_qualification.exists():
                        return Response({'status': '이미 신고된 글 입니다'}, status=403)
                    
                except Community_Articles.DoesNotExist:
                    return Response('article does not exist')
                
            elif reporting_content_type == 'comment':
                try:

                    selected_comment = Community_Article_Comment.objects.get(id=reporting_id)
                    reporting_data['reported_comment'] = selected_comment

                    reporting_qualification = ReportedArticlesComments.objects.filter(
                        reported_user=user, 
                        reported_comment=selected_comment
                    )

                    if reporting_qualification.exists():
                        return Response({'status': '이미 신고된 댓글 입니다'}, status=403)
                    
                except Community_Article_Comment.DoesNotExist:
                    return Response('comments does not exist')
            elif reporting_content_type == 'comment_reply':
                try:

                    selected_comment_reply = Community_Article_Comment_Reply.objects.get(id=reporting_id)
                    reporting_data['reported_comment_reply'] = selected_comment_reply

                    reporting_qualification = ReportedArticlesComments.objects.filter(
                        reported_user=user, 
                        reported_comment_reply=selected_comment_reply
                    )

                    if reporting_qualification.exists():
                        return Response({'status': '이미 신고된 댓글 입니다'}, status=403)
                    
                except Community_Article_Comment.DoesNotExist:
                    return Response('reply does not exist')
                

            

            reporting_form = ReportedArticlesCommentsForm(reporting_data)

            if reporting_form.is_valid():
                report = reporting_form.save()
                
                if user_id and user:
                    report.reported_user = user
                    report.save()

                return Response({'status': 'article has been reported'}, status=200)
            
            else:
                return Response({'status': 'article reporting error'}, status=404)
            
    else:
        return Response({'status': 'not authorized'}, status=401)

