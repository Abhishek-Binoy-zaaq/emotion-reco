"""
Check video status
Run with: type check_videos.py | python manage.py shell
"""

from quickstart.models import Video

print("\n=== Video Status ===\n")
videos = Video.objects.all()

if not videos:
    print("No videos found!")
else:
    for video in videos:
        print(f"ID: {video.id}")
        print(f"Title: {video.title}")
        print(f"Is Active: {video.is_active}")
        print(f"File: {video.video_file}")
        print("-" * 40)

print(f"\nTotal videos: {videos.count()}")
print(f"Active videos: {Video.objects.filter(is_active=True).count()}")
