from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


# Company Announcement
from .models import Company_Announcement
from .serializers import CompanyAnnouncementSerializers, CompanyAnnouncementSimpleSerializers

# Rest
from rest_framework.decorators import api_view
from rest_framework.response import Response

# Create your views here.

@api_view(['GET'])
def GetCompanyAnnouncements(request):
    search_kw = request.GET.get('kw')
    
    search_filter = Q()
    if search_kw:
        search_filter = Q(Company_Announcement_Subject__contains=search_kw) | Q(Company_Announcement_Content__contains=search_kw)


    announcement = Company_Announcement.objects.filter(search_filter).order_by('-Company_Announcement_Date')

    page = request.GET.get('page')
    paginator = Paginator(announcement, 10)

    try:
        filtered_announcement = paginator.page(page)
    except PageNotAnInteger:
        filtered_announcement = paginator.page(1)
    except EmptyPage:
        filtered_announcement = paginator.page(paginator.num_pages)

    serializer = CompanyAnnouncementSimpleSerializers(filtered_announcement, many=True)

    return Response({
        'announcements': serializer.data,
        'max_page': paginator.num_pages,
        'current_page': page
    })

@api_view(['GET'])
def GetAnnouncementDetail(request, announcement_id):
    announcement = Company_Announcement.objects.get(id=announcement_id)
    serializer = CompanyAnnouncementSerializers(announcement)
    return Response(serializer.data)