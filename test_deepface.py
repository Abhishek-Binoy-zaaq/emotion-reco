"""
Test DeepFace installation
Run with: python test_deepface.py
"""

try:
    from deepface import DeepFace
    print("✓ DeepFace imported successfully")
    
    # Try to analyze a test image
    print("\nTesting emotion detection...")
    print("This will download models on first run (may take a few minutes)...")
    
    # You can test with one of your captured images
    # Replace with an actual image path from media/captures/
    test_image = "media/captures/capture_1763454202741.jpg"
    
    result = DeepFace.analyze(
        img_path=test_image,
        actions=['emotion'],
        enforce_detection=False,
        detector_backend='opencv',
        silent=False
    )
    
    print("\n✓ Detection successful!")
    print(f"Result: {result}")
    
except Exception as e:
    print(f"\n✗ Error: {e}")
    print("\nTry installing: pip install opencv-python-headless")
