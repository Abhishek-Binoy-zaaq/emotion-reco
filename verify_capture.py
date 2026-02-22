
import cv2
import os
import sys
import numpy as np

# Setup Django environment
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings') 
import django
django.setup()

from emotions.image_preprocessing import EnhancedEmotionDetectionService

def verify_capture_and_accuracy():
    print("=== Manual Verification of Capture and Accuracy ===")
    
    # 1. Look for a recent capture to test with (Original capture, not preprocessed)
    captures_dir = os.path.join(os.getcwd(), 'media', 'captures')
    
    # Get the most recent file that does NOT contain "preprocessed"
    files = [
        os.path.join(captures_dir, f) 
        for f in os.listdir(captures_dir) 
        if f.endswith('.jpg') and 'preprocessed' not in f
    ]
    
    if not files:
        print("No original captures found in media/captures.")
        return
    
    test_image_path = max(files, key=os.path.getctime)
    
    # 2. Run the pipeline
    with open('verify_capture_output.txt', 'w') as f:
        f.write(f"Running analysis on: {test_image_path}\n")
        
        # Force save of preprocessed image to debug crop
        result = EnhancedEmotionDetectionService.analyze_image_with_preprocessing(
            test_image_path, 
            save_preprocessed=True
        )
        
        f.write("\n=== Analysis Results ===\n")
        f.write(f"Success: {result['success']}\n")
        f.write(f"Face Detected: {result['face_detected']}\n")
        if result['success']:
             f.write(f"Expression: {result['expression']}\n")
             f.write(f"Confidence: {result['confidence']}\n")
             f.write(f"All Emotions: {result['all_emotions']}\n")
             
             if result['preprocessed_path'] and os.path.exists(result['preprocessed_path']):
                 f.write(f"[OK] Preprocessed image saved at: {result['preprocessed_path']}\n")
        else:
             f.write(f"Error: {result['error']}\n")

if __name__ == "__main__":
    verify_capture_and_accuracy()
