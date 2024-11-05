from django.conf import settings
import os
import re

# Bad Word + Sensitive information filtering system
def sensitive_content_filtering(content):
    try:
        #BadWord DB call
        file_path = os.path.join(settings.BASE_DIR, 'BadWordFilter.txt')
        #BadWord Filtering
        with open(file_path, 'r', encoding='utf-8') as file:
            bad_words = file.read().splitlines()
            for word in bad_words:
                if word in content:
                    content = content.replace(word, "*" * len(word))

        # Email Filtering
        email_regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        content = re.sub(email_regex, '[개인정보 보호을 위해 가려진 컨텐츠입니다]', content)

        # Mobile Number Filtering
        phone_regex = r'(\d{3}[-.\s]?\d{4}[-.\s]?\d{4})|(\d{2,3}[-.\s]?\d{3,4}[-.\s]?\d{4})'
        content = re.sub(phone_regex, '[개인정보 보호을 위해 가려진 컨텐츠입니다]', content)

        
        return re.sub(r'<span\s+style="color:\s*rgb\(0,\s*0,\s*0\);">', '<span>', content)

    except FileNotFoundError:
        print("Error: BadWordFilter.txt file not found.")