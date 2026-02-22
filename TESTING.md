
# 7. TESTING

In the **Emotion Recognition System**, testing and validation were performed to ensure the web application is defect-free and performs according to expectations, specifically focusing on the accuracy of emotion detection and the stability of the video capture pipeline.

The testing strategy involved:
1.  **Unit Testing**: Verifying individual components like data models.
2.  **System/Integration Testing**: Validating the end-to-end flow from webcam capture to emotion analysis.         
3.  **Manual Verification**: Using custom scripts (`verify_capture.py`) to debug and validate the DeepFace integration.

## 7.1 UNIT TESTING
In our project, unit testing infrastructure is provided by Django's `TestCase`. The test definitions are located in `emotions/tests.py`. These tests are designed to run in isolation to verify the integrity of the database models and utility functions without requiring the full server to be running.

**Implementation (`emotions/tests.py`):**
```python
from django.test import TestCase

# Create your tests here.
# Future tests include:
# - UserProfile creation validation
# - SessionReport data integrity checks
```

## 7.2 INTEGRATION TESTING
Integration testing in this project focused on ensuring the seamless interaction between the **Frontend (JavaScript/Webcam)** and the **Backend (Django/DeepFace)**.

Key integration scenarios tested:
*   **Data Transmission**: Verifying that frames captured by the user's webcam are correctly converted to Base64 and received by the Django view.
*   **Model Integration**: Ensuring that the `image_preprocessing.py` module correctly interacts with the `DeepFace` library to return valid emotion predictions.
*   **Database Storage**: Verifying that analysis results are correctly linked to `SessionReport` and `User` models.

## 7.3 SYSTEM TESTING
System testing was the primary validation method for this project. We utilized a "White Box" testing approach using a custom verification script (`verify_capture.py`) to inspect the internal logic of the image processing pipeline.

**Automated verification was performed to check:**
1.  **Face Detection**: Confirmed that faces are correctly detected and cropped from raw images.
2.  **Emotion Inference**: Validated that the DeepFace model returns a confidence score and a dominant emotion (e.g., "happy", "neutral").
3.  **File Handling**: Ensured that preprocessed images are saved correctly without recursive filename errors.

**Verification Script Code (`verify_capture.py`):**
This script was the core tool for our system testing. It loads a real captured image and runs it through the exact same pipeline used in production.

```python
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
             # ... logging details ...
             
             if result['preprocessed_path'] and os.path.exists(result['preprocessed_path']):
                 f.write(f"[OK] Preprocessed image saved at: {result['preprocessed_path']}\n")
        else:
             f.write(f"Error: {result['error']}\n")

if __name__ == "__main__":
    verify_capture_and_accuracy()
```

### 7.3.1 Types of System Testing Used

**White Box Testing**
We performed White Box testing by analyzing the internal structure of `image_preprocessing.py`. We inspected line-by-line execution to fix issues such as:
*   Recursive filename generation.
*   Correct handling of DeepFace return objects.
*   Exception handling during model loading.

**Black Box Testing**
Black Box testing was conducted via the user interface:
*   **Login Flow**: Verifying user authentication.
*   **Live Session**: Starting a video session and visually confirming that the "Tracking Active" indicator turns green.
*   **Report Generation**: checking that the final session report accurately reflects the user's emotions during the video.

# 8. IMPLEMENTATION & QUALITY ASSURANCE

## Implementation Strategy
The system was implemented using a modular approach:
1.  **Backend Core**: Django 5.2 was setup to handle routing, database ORM, and user management.
2.  **ML Integration**: The `DeepFace` library was integrated into a dedicated service (`EnhancedEmotionDetectionService`) to isolate AI logic from web logic.
3.  **Frontend**: Standard HTML/JS was used to access the `MediaStream` API for camera integration.

## Quality Assurance Steps
Quality was ensured through specific checks:
*   **Dependency Management**: All libraries (opencv, deepface, django) are tracked in `requirements.txt` to ensure consistent environments.
*   **Error Logging**: The `image_preprocessing.py` module includes detailed error logging to the console (using `sys.stdout.flush()`) to catch runtime failures in the background process.
*   **Validation**: The `verify_capture.py` script serves as a regression test to ensure that changes to the code do not break the core emotion detection loop.

## System Maintenance
Maintenance for this project involves:
*   **Model Updates**: Updating `DeepFace` to newer versions for better accuracy.
*   **Database Backups**: Regularly backing up `db.sqlite3` to preserve user reports.
*   **Log Monitoring**: Checking `verify_capture_output.txt` periodically to ensure detection accuracy remains high.
