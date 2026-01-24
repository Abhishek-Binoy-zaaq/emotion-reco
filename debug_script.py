
from emotions.models import SessionReport, CapturedFrame, PreprocessedImage

def inspect_latest_sessions():
    print("Inspecting latest 5 sessions...")
    sessions = SessionReport.objects.all().order_by('-started_at')[:5]
    
    for session in sessions:
        print(f"\nSession ID: {session.id}, User: {session.user.username}, Video: {session.video.title if session.video else 'None'}")
        print(f"Created: {session.started_at}, Completed: {session.is_completed}")
        
        captures = session.captures.all()
        print(f"Total Captures (frames): {captures.count()}")
        
        preprocessed_count = 0
        for capture in captures:
            try:
                if hasattr(capture, 'preprocessed_version'):
                    preprocessed_count += 1
            except Exception as e:
                pass
                
        print(f"Preprocessed Images: {preprocessed_count}")
        
        # Check actual PreprocessedImage objects filtered by session
        calc_preprocessed = PreprocessedImage.objects.filter(session=session).count()
        print(f"PreprocessedImage objects (direct filter): {calc_preprocessed}")
        
        summary = session.get_emotion_summary()
        print(f"Emotion Summary Result: {summary}")

inspect_latest_sessions()
