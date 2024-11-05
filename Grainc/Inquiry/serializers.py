from rest_framework import serializers
from django.template.defaultfilters import linebreaksbr


from .models import Inquiry

class InquirySerializer(serializers.ModelSerializer):
    class Meta:
        model = Inquiry
        fields = '__all__' 
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['inquiry_id'] = instance.id
        data['formatted_inquiry_date'] = instance.Inquiry_date.strftime('%Y.%m.%d:%H.%M.%S')
        data['formatted_inquiry_main_content'] = linebreaksbr(instance.Inquiry_main_content)

        if instance.Inquiry_reply_date:
            formatted_inquiry_reply_date = instance.Inquiry_reply_date.strftime('%Y.%m.%d:%H.%M.%S')
        else:
            formatted_inquiry_reply_date = None
        data['formatted_inquiry_reply_date'] = formatted_inquiry_reply_date

        if instance.Inquiry_main_content:
            formatted_Inquiry_reply = linebreaksbr(instance.Inquiry_reply)
        else:
            formatted_Inquiry_reply = None
        data['formatted_Inquiry_reply'] = formatted_Inquiry_reply
        return data