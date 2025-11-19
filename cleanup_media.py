"""
Clean up database records for missing media files
Run with: type cleanup_media.py | python manage.py shell
"""

import os
from django.conf import settings
from quickstart.models import Video, VideoSession, CapturedFrame, UploadedImage

# Check if media folder exists
media_root = settings.MEDIA_ROOT
print(f"Media folder: {media_root}")
print(f"Media folder exists: {os.path.exists(media_root)}")

# Delete all captured frames
frame_count = CapturedFrame.objects.count()
CapturedFrame.objects.all().delete()
print(f'✓ Deleted {frame_count} captured frames')

# Delete all sessions
session_count = VideoSession.objects.count()
VideoSession.objects.all().delete()
print(f'✓ Deleted {session_count} video sessions')

# Delete all videos
video_count = Video.objects.count()
Video.objects.all().delete()
print(f'✓ Deleted {video_count} videos')

# Delete all uploaded images
image_count = UploadedImage.objects.count()
UploadedImage.objects.all().delete()
print(f'✓ Deleted {image_count} uploaded images')

print('\n✅ Database cleaned!')
print('\nNext steps:')
print('1. Create media folder: mkdir media')
print('2. Upload new videos through Admin → Manage Videos')
print('3. Start fresh video sessions')
