import os
import django
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings') 
django.setup()

from rest_framework.test import APIClient
from django.contrib.auth.models import User
from emotions.models import Video, VideoCategory, SessionReport

def reproduce_issue():
    # 1. Setup User and Client
    user, _ = User.objects.get_or_create(username='test_debug_user')
    client = APIClient()
    client.force_authenticate(user=user)
    
    # 2. Setup Dummy Data
    category, _ = VideoCategory.objects.get_or_create(name='Debug Cat')
    video, _ = Video.objects.get_or_create(
        title='Debug Video',
        defaults={
            'category': category,
            'duration': 100,
            'uploaded_by': user,
            'video_file': 'videos/dummy.mp4' # Dummy path
        }
    )
    
    # 3. Create Session
    response = client.post('/api/sessions/', {'video': video.id}, format='json')
    if response.status_code != 201:
        print(f"Failed to create session: {response.content}")
        return
        
    session_id = response.data['id']
    print(f"Created Session {session_id}")
    
    # 4. Simulate Params
    # Minimal JPEG header
    dummy_image_content = b'\xFF\xD8\xFF\xE0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xFF\xDB\x00C\x00\xFF\xC0\x00\x11\x08\x00\x01\x00\x01\x03\x01\x22\x00\x02\x11\x01\x03\x11\x01\xFF\xC4\x00\x1F\x00\x00\x01\x05\x01\x01\x01\x01\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0A\x0B\xFF\xDA\x00\x0C\x03\x01\x00\x02\x11\x03\x11\x00\x3F\x00\xBF\xFF\xD9' 
    
    image = SimpleUploadedFile("test_capture.jpg", dummy_image_content, content_type="image/jpeg")
    
    data = {
        'session': session_id,
        'timestamp': 1.5,
        'image': image
    }
    
    print("Uploading capture...")
    res = client.post('/api/captures/', data, format='multipart')
    
    print("\n=== API RESPONSE ===")
    import json
    # Use default=str to handle non-serializable objects if any
    print(json.dumps(res.data, indent=2, default=str))
    print("====================")

if __name__ == "__main__":
    reproduce_issue()
