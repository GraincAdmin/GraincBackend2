from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
# Announcement Model
from .models import Announcement
# Announcement Serializer 
from .serializers import AnnouncementSerializer, ImportanceAnnouncementSerializer
# Create your views here.


@api_view(['GET'])
@permission_classes([AllowAny])

def GetImportantAnnouncement(request):
    # Fetch the most recent important announcement that has ended
    announcement = Announcement.objects.filter(
        end_time__gt=timezone.now(),
        is_important=True
    ).order_by('-create_date').first()  # Using .first() to get the single instance or None

    if (announcement):
        serializer = ImportanceAnnouncementSerializer(announcement)
        return Response(serializer.data)
    else:
        return Response(status=200)

    
@api_view(['GET'])
def GetAnnouncement(request):
    announcements = Announcement.objects.order_by('-create_date')

    page = request.GET.get('page')
    paginator = Paginator(announcements, 10)
    
    try:
        paginated_announcement = paginator.page(page)
    except PageNotAnInteger:
        paginated_announcement = paginator.page(1)
    except EmptyPage:
        paginated_announcement = paginator.page(paginator.num_pages)


    serializer = AnnouncementSerializer(paginated_announcement, many=True)

    return Response({
        'announcement': serializer.data,
        'max_page': paginator.num_pages,
        'current_page': page
    })

@api_view(['GET'])
def GetAnnouncementDetail(request, announcement_id):
    
    announcement = Announcement.objects.get(id=announcement_id)

    serializer = AnnouncementSerializer(announcement)

    return Response(serializer.data)