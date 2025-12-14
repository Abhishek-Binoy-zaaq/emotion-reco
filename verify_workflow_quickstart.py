
import os
import django
import sys
from pathlib import Path
import cv2
import numpy as np

# Setup Django environment
sys.path.append(r'c:\Users\abhis\tutorials')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tutorials.settings')
django.setup()

from quickstart.models import CapturedFrame, PreprocessedImage, VideoSession, Video
from django.contrib.auth.models import User
from quickstart.services import EmotionDetectionService, SessionAnalyticsService
from django.conf import settings

def create_test_image(filename="test_face.jpg"):
    # Create a dummy image with a face-like structure (white circle on black background)
    # Note: DeepFace might not detect this as a face, so we might need a real image or mock the detection.
    # Since we can't easily upload a real face image here, we will try to rely on the fact that we can mock 
    # or we will just test the logic flow and handle "no face detected" as a valid outcome for the logic test.
    
    # Better yet, let's create a dummy image file.
    img = np.zeros((300, 300, 3), dtype=np.uint8)
    cv2.circle(img, (150, 150), 100, (255, 255, 255), -1) # Draw a circle
    
    path = os.path.join(settings.MEDIA_ROOT, 'captures', filename)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    cv2.imwrite(path, img)
    return path

def verify_workflow():
    print("Verifying workflow...")
    
    # 1. Setup Data
    user, _ = User.objects.get_or_create(username='test_verifier')
    video, _ = Video.objects.get_or_create(title='Test Video', duration=100, uploaded_by=user)
    session = VideoSession.objects.create(user=user, video=video)
    
    # 2. Create CapturedFrame
    image_path = create_test_image()
    # Path relative to media root
    rel_path = os.path.relpath(image_path, settings.MEDIA_ROOT)
    
    capture = CapturedFrame.objects.create(
        session=session,
        image=rel_path,
        timestamp=10.5
    )
    print(f"Created capture: {capture}")
    
    # Check CapturedFrame fields - should NOT have emotion fields
    if hasattr(capture, 'expression'):
        print("FAIL: CapturedFrame still has 'expression' field!")
    else:
        print("PASS: CapturedFrame does not have 'expression' field.")
        
    # 3. Simulate Analysis (Service Call)
    # We will mock ImagePreprocessor.preprocess_image to return success even for our dummy image
    # to test the database logic.
    
    from quickstart.image_preprocessing import ImagePreprocessor
    
    # Backup original
    original_preprocess = ImagePreprocessor.preprocess_image
    
    # Mock
    def mock_preprocess(image_path, save_preprocessed=False):
        # Return a fake success result
        return {
            'success': True,
            'preprocessed_image': np.zeros((100, 100, 3), dtype=np.uint8),
            'face_detected': True,
            'face_coordinates': {'x': 0, 'y': 0, 'width': 100, 'height': 100},
            'preprocessed_path': image_path.replace('captures', 'preprocessed'), # Fake path
            'error': None
        }
    
    ImagePreprocessor.preprocess_image = mock_preprocess
    
    # Also mock detect_emotion since we don't have a real face
    from quickstart.services import EmotionDetectionService
    # We can't easily mock the method inside the service without monkeypatching, 
    # but the service calls DeepFace. We can mock DeepFace or just the result in the calling code?
    # The calling code is `EmotionDetectionService.analyze_image`.
    # Let's actually call the service but with a mocked DeepFace?
    # Or simpler: we can just call the VIEW logic concept here.
    
    # Let's recreate what the View does:
    print("Simulating View Logic...")
    
    # Create a preprocessed image based on our mock result "happy"
    # In the real view, this happens after analyze_image returns success.
    # So we need analyze_image to return success.
    
    # Let's mock analyze_image to return a success so we can test the saving logic.
    original_analyze = EmotionDetectionService.analyze_image
    
    def mock_analyze(image_path, save_preprocessed=False):
        return {
            'success': True,
            'expression': 'happy',
            'confidence': 99.9,
            'all_emotions': {'happy': 99.9, 'sad': 0.1},
            'preprocessed_path': os.path.join(settings.MEDIA_ROOT, 'preprocessed', 'test_face.jpg'),
            'error': None
        }
        
    EmotionDetectionService.analyze_image = mock_analyze
    
    # Run the logic that's in the View
    analysis_result = EmotionDetectionService.analyze_image(capture.image.path, save_preprocessed=True)
    
    if analysis_result['success']:
        print("Analysis successful (mocked).")
        
        # This is the logic we added to the View
        preprocessed_path = analysis_result.get('preprocessed_path')
        if preprocessed_path:
            rel_path_prep = "preprocessed/test_face.jpg" # simplified
            
            # Ensure model saves correctly
            preprocessed_obj = PreprocessedImage.objects.create(
                capture=capture,
                image=rel_path_prep,
                expression=analysis_result['expression'],
                expression_confidence=analysis_result['confidence'],
                all_expressions=analysis_result['all_emotions']
            )
            print(f"Created PreprocessedImage: {preprocessed_obj}")
            
            # Verify fields
            print(f"Stored Expression: {preprocessed_obj.expression}")
            if preprocessed_obj.expression == 'happy':
                print("PASS: Expression stored correctly.")
            else:
                print(f"FAIL: Expected 'happy', got {preprocessed_obj.expression}")
    
    # 4. Verify Session Analytics
    print("Verifying Session Analytics...")
    report = SessionAnalyticsService.generate_session_report(session)
    print("Session Report:", report)
    
    detection_rate = report.get('detection_rate')
    if detection_rate == 100.0: # 1 capture, 1 success
        print("PASS: Session report calculated correctly using PreprocessedImage data.")
    else:
        print(f"FAIL: Session report detection rate incorrect: {detection_rate}")

    # Restore mocks (not strictly necessary as script ends, but good practice)
    ImagePreprocessor.preprocess_image = original_preprocess
    EmotionDetectionService.analyze_image = original_analyze
    
    print("Verification Complete.")

if __name__ == "__main__":
    verify_workflow()
