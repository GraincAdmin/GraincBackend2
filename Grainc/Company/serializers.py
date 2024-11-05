from rest_framework import serializers
from .models import Company_Announcement


class CompanyAnnouncementSimpleSerializers(serializers.ModelSerializer):
    class Meta:
        model = Company_Announcement
        fields = ('Company_Announcement_Date', 'Company_Announcement_Subject')
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['announcement_id'] = instance.id
        data['formatted_create_date'] = instance.Company_Announcement_Date.strftime('%Y.%m.%d:%H.%M.%S')
        return data


class CompanyAnnouncementSerializers(serializers.ModelSerializer):
    class Meta:
        model = Company_Announcement
        fields = '__all__'
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['formatted_create_date'] = instance.Company_Announcement_Date.strftime('%Y.%m.%d:%H.%M.%S')
        return data