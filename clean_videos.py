"""
Delete all video records from database
Run with: type clean_videos.py | python manage.py shell
"""

from quickstart.models import Video, VideoSession, CapturedFrame

# Delete all captured frames
CapturedFrame.objects.all().delete()
print('✓ Deleted all captured frames')

# Delete all sessions
VideoSession.objects.all().delete()
print('✓ Deleted all video sessions')

# Delete all videos
Video.objects.all().delete()
print('✓ Deleted all videos')

print('\n✅ Database cleaned! All video records removed.')
