
from django.core.management.base import BaseCommand
from emotions.models import SessionReport, CapturedFrame, PreprocessedImage

class Command(BaseCommand):
    help = 'Inspects the latest sessions for data integrity'

    def handle(self, *args, **kwargs):
        self.stdout.write("Inspecting latest 5 sessions...")
        sessions = SessionReport.objects.all().order_by('-started_at')[:5]
        
        for session in sessions:
            self.stdout.write(f"\nSession ID: {session.id}, User: {session.user.username}, Video: {session.video.title if session.video else 'None'}")
            self.stdout.write(f"Created: {session.started_at}, Completed: {session.is_completed}")
            self.stdout.write(f"Session Report Field (Dominant): {session.session_report}")
            self.stdout.write(f"Cached Report Data (keys): {list(session.report_data.keys()) if session.report_data else 'None'}")
            
            captures = session.captures.all()
            self.stdout.write(f"Total Captures (frames): {captures.count()}")
            
            preprocessed_count = 0
            for capture in captures:
                try:
                    if hasattr(capture, 'preprocessed_version'):
                        preprocessed_count += 1
                except Exception:
                    pass
                    
            self.stdout.write(f"Preprocessed Images: {preprocessed_count}")
            
            summary = session.get_emotion_summary()
            self.stdout.write(f"Emotion Summary Result: {summary}")
