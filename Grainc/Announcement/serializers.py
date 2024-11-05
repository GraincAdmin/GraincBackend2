from rest_framework import serializers
from django.template.defaultfilters import linebreaksbr

from .models import Announcement

class AnnouncementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Announcement
        fields = '__all__'

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['announcement_id'] = instance.id
        data['formatted_create_date'] = instance.create_date.strftime('%Y.%m.%d:%H.%M.%S')
        data['formatted_announcement'] = linebreaksbr(instance.content)
        return data
    
class ImportanceAnnouncementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Announcement
        fields = ('id', 'start_time', 'end_time', 'subject')

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['formatted_start_time'] = instance.start_time.strftime('%Y.%m.%d:%H.%M')
        data['formatted_end_time'] = instance.end_time.strftime('%Y.%m.%d:%H.%M')
        return data