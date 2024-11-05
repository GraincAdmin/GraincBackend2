from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from bs4 import BeautifulSoup
import base64
import uuid  # Import the uuid module
import re
from django.conf import settings
from io import BytesIO
from PIL import Image
import random
import string
"""
S3 Library
"""
import boto3
from urllib.parse import urlparse
# Content Models
from Community.models import Community_Articles

def RandomFolderName(length=10):
    characters = string.ascii_letters + string.digits  # Includes letters and digits
    return ''.join(random.choice(characters) for i in range(length))


def QuillImageProcessor(content_type, main_content, s3_folder_path, user_pk):

    if content_type == 'community':
        content_folder = 'user_uploaded_articles'
        
    elif content_type == 'report':
        content_folder = 'user_uploaded_reports'


    soup = BeautifulSoup(main_content, 'html.parser')
    images = soup.find_all('img')

    for img in images:
        src = img.get('src', '')
        if src.startswith('data:image/'):
            # Extract Base64 data
            header, encoded = src.split(',', 1)
            data = base64.b64decode(encoded)

            # Determine file type and extension
            image_format = re.search(r'data:image/([^;]+);', header).group(1)
            file_extension = {'jpeg': 'jpg', 'png': 'png', 'gif': 'gif'}.get(image_format, 'jpg')
            file_name = f'{uuid.uuid4()}.{file_extension}'

            data = compress_image(data)

            # Define the file path for S3
            if content_type == 'community':
                file_path = f'{content_folder}/{user_pk}/{s3_folder_path}/{file_name}'
            elif content_type == 'report':
                file_path = f'{content_folder}/{user_pk}/{s3_folder_path}/description/{file_name}'

            s3_client = boto3.client(
                's3',
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_S3_REGION_NAME
            )

            # Save the image to S3
            # saved_path = default_storage.save(file_path, ContentFile(data))
            s3_client.put_object(
                Bucket=settings.AWS_STORAGE_BUCKET_NAME,
                Key=file_path,
                Body=data,  # Use raw data (binary), not ContentFile
                ContentType=f'image/{image_format}',  # Add content type for proper S3 handling
                ACL='public-read'  # Optional: make file publicly accessible
            )

            # Generate the S3 URL
            file_url = f'https://{settings.AWS_S3_CUSTOM_DOMAIN}/{file_path}'
            # default_storage.url(saved_path)

            # Replace Base64 source with the S3 URL
            img['src'] = file_url

    return str(soup)

def QuillImageProcessorModification(content_type, previous_main_content, new_main_content, s3_folder_path, user_pk):
    s3_client = boto3.client('s3')
    bucket_name = settings.AWS_STORAGE_BUCKET_NAME
    """
    default new folder path
    """
    # Parse previous and new content
    previous_soup = BeautifulSoup(previous_main_content, 'html.parser')
    previous_images = {img.get('src') for img in previous_soup.find_all('img')}

    new_content_with_images = QuillImageProcessor(content_type, new_main_content, s3_folder_path, user_pk)
    new_soup = BeautifulSoup(new_content_with_images, 'html.parser')
    new_images = {img.get('src') for img in new_soup.find_all('img')}

    # Determine which images were in the previous content but not in the new content
    images_to_delete = previous_images - new_images

    # Delete the removed images
    for img_src in images_to_delete:
        # Extract file path within the S3 bucket from the URL
        parsed_url = urlparse(img_src)
        s3_key = parsed_url.path.lstrip('/')  # Remove leading slash from path
        
        try:
            s3_client.delete_object(Bucket=bucket_name, Key=s3_key)
            print(f"Deleted: {s3_key}")
        except Exception as e:
            print(f"Error deleting {s3_key}: {e}")

    return str(new_soup)

def QuillContentDelete(content_type, content_id):
    s3_client = boto3.client('s3')
    bucket_name = settings.AWS_STORAGE_BUCKET_NAME
    if content_type == 'community':
        selected_article = Community_Articles.objects.get(id=content_id)

        article_content = selected_article.main_content
        article_soup = BeautifulSoup(article_content, 'html.parser')
        article_images = {img.get('src') for img in article_soup.find_all('img')}

        for img_src in article_images:
            parsed_url = urlparse(img_src)
            s3_key = parsed_url.path.lstrip('/')
            try:
                s3_client.delete_object(Bucket=bucket_name, Key=s3_key)
                print(f"Deleted: {s3_key}")
            except Exception as e:
                print(f"Error deleting {s3_key}: {e}")

                      


def extract_img_urls(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    images = soup.find_all('img')[:1]
    if not images:
        return None
    else:
        return [img['src'] for img in images[:1]]
    

def compress_image(data, max_file_size_mb=5, initial_quality=95, min_quality=10):
    """
    Compress image data to ensure it is below the specified file size.
    """
    quality = initial_quality
    while quality >= min_quality:
        # Load image from binary data
        image = Image.open(BytesIO(data))

        # Save image to a BytesIO object with current quality
        buffer = BytesIO()
        image.save(buffer, format=image.format, quality=quality, optimize=True)
        compressed_data = buffer.getvalue()

        # Check the file size
        if len(compressed_data) <= max_file_size_mb * 1024 * 1024:  # Convert MB to bytes
            return compressed_data
        
        # Reduce quality for next iteration
        quality -= 5

    return compressed_data

def compress_image_flutter(file, max_file_size_mb=5, initial_quality=95, min_quality=10):
    """
    Compress image data to ensure it is below the specified file size.
    """
    quality = initial_quality
    while quality >= min_quality:
        # Load image from binary data
        file.seek(0)  # Reset file pointer to the start
        image = Image.open(file)

        # Save image to a BytesIO object with current quality
        buffer = BytesIO()
        image.save(buffer, format=image.format, quality=quality, optimize=True)
        compressed_data = buffer.getvalue()

        # Check the file size
        if len(compressed_data) <= max_file_size_mb * 1024 * 1024:  # Convert MB to bytes
            return compressed_data
        
        # Reduce quality for next iteration
        quality -= 5

    return compressed_data