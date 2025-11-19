"""
Script to activate all videos
Run with: python manage.py shell < fix_videos.py
"""

from quickstart.models import Video

# Activate all videos
videos = Video.objects.all()
count = videos.update(is_active=True)

print(f'✓ Activated {count} videos')
print('\nAll videos are now active and will appear in the dashboard!')
