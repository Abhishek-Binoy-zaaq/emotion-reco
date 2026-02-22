"""
Image Preprocessing Pipeline for Emotion Detection
Optimized for speed and accuracy by letting DeepFace handle the full pipeline.
"""
import cv2
import numpy as np
from pathlib import Path
import sys
from deepface import DeepFace

# Emotion labels supported by DeepFace
EMOTION_LABELS = ['angry', 'disgust', 'fear', 'happy', 'neutral', 'sad', 'surprise']

# Flag to track if models have been warmed up
_models_warmed_up = False


def warmup_models():
    """
    Pre-load DeepFace models at startup to avoid cold-start delay.
    Call this once when the Django app starts.
    """
    global _models_warmed_up
    if _models_warmed_up:
        return
    
    try:
        print("[WARMUP] Pre-loading emotion detection models...", flush=True)
        # Create a small dummy image to trigger model loading
        dummy = np.zeros((100, 100, 3), dtype=np.uint8)
        dummy[30:70, 30:70] = 128  # Gray square
        
        # This will fail to find a face but will load the detector and emotion models
        try:
            DeepFace.analyze(
                img_path=dummy,
                actions=['emotion'],
                detector_backend='opencv',
                enforce_detection=False,
                silent=True
            )
        except:
            pass
        
        _models_warmed_up = True
        print("[WARMUP] Models loaded successfully!", flush=True)
    except Exception as e:
        print(f"[WARMUP] Warning: Could not pre-load models: {e}", flush=True)


class EnhancedEmotionDetectionService:
    """
    Fast and accurate emotion detection service.
    
    Uses DeepFace.analyze() directly on raw images, which:
    1. Properly aligns faces before emotion analysis (better accuracy)
    2. Uses opencv detector by default (much faster than retinaface)
    """
    
    # Backends ordered by speed (fastest first)
    # opencv: ~0.1s, ssd: ~0.5s, mtcnn: ~1s, retinaface: ~3-5s
    BACKENDS = ['opencv', 'ssd', 'mtcnn']
    
    # Padding around face for saved preprocessed image
    FACE_PADDING = 0.15
    
    @staticmethod
    def analyze_image_with_preprocessing(image_path, save_preprocessed=False):
        """
        Analyze image for facial emotion using DeepFace's full pipeline.
        
        This is faster and more accurate than manual preprocessing because
        DeepFace handles face alignment internally before emotion analysis.
        
        Args:
            image_path: Path to the input image
            save_preprocessed: Whether to save the cropped face image
            
        Returns:
            dict with success, expression, confidence, all_emotions, etc.
        """
        result = {
            'success': False,
            'face_detected': False,
            'face_coordinates': None,
            'expression': None,
            'confidence': None,
            'all_emotions': None,
            'preprocessed_path': None,
            'error': None
        }
        
        image_path = str(image_path)
        
        # Try each backend until one works
        for backend in EnhancedEmotionDetectionService.BACKENDS:
            try:
                # Single call handles: face detection → alignment → emotion analysis
                analysis = DeepFace.analyze(
                    img_path=image_path,
                    actions=['emotion'],
                    detector_backend=backend,
                    enforce_detection=True,
                    silent=True
                )
                
                # Handle list response
                if isinstance(analysis, list):
                    analysis = analysis[0]
                
                # Extract emotion data
                emotions = analysis.get('emotion', {})
                dominant = analysis.get('dominant_emotion', 'unknown')
                region = analysis.get('region', {})
                
                if not emotions or dominant == 'unknown':
                    continue
                
                # Success! Populate result
                result['success'] = True
                result['face_detected'] = True
                result['expression'] = dominant
                result['confidence'] = float(emotions.get(dominant, 0))
                result['all_emotions'] = {k: float(v) for k, v in emotions.items()}
                result['face_coordinates'] = {
                    'x': region.get('x', 0),
                    'y': region.get('y', 0),
                    'width': region.get('w', 0),
                    'height': region.get('h', 0)
                }
                
                # Save cropped face if requested
                if save_preprocessed and region:
                    preprocessed_path = EnhancedEmotionDetectionService._save_face_crop(
                        image_path, region
                    )
                    result['preprocessed_path'] = preprocessed_path
                
                print(f"[OK] {backend}: {dominant} ({result['confidence']:.1f}%)", flush=True)
                return result
                
            except Exception as e:
                # Try next backend
                continue
        
        # All backends failed
        result['error'] = 'No face detected'
        print(f"[FAIL] No face detected with any backend", flush=True)
        return result
    
    @staticmethod
    def _save_face_crop(image_path, region):
        """Save a cropped face image for display/records."""
        try:
            image = cv2.imread(image_path)
            if image is None:
                return None
            
            x = region.get('x', 0)
            y = region.get('y', 0)
            w = region.get('w', 0)
            h = region.get('h', 0)
            
            if w == 0 or h == 0:
                return None
            
            # Add padding
            pad = EnhancedEmotionDetectionService.FACE_PADDING
            px, py = int(w * pad), int(h * pad)
            
            x1 = max(0, x - px)
            y1 = max(0, y - py)
            x2 = min(image.shape[1], x + w + px)
            y2 = min(image.shape[0], y + h + py)
            
            crop = image[y1:y2, x1:x2]
            
            # Generate output path
            p = Path(image_path)
            stem = p.stem
            if not stem.endswith('_preprocessed'):
                new_name = f"{stem}_preprocessed{p.suffix}"
            else:
                new_name = p.name
            
            output_path = str(p.parent / new_name)
            cv2.imwrite(output_path, crop)
            
            return output_path
            
        except Exception as e:
            print(f"[WARN] Could not save face crop: {e}", flush=True)
            return None


# Legacy class kept for compatibility but now just wraps the enhanced service
class ImagePreprocessor:
    """Legacy preprocessor - now wraps EnhancedEmotionDetectionService."""
    
    MIN_FACE_SIZE = (48, 48)
    FACE_PADDING = 0.15
    
    @staticmethod
    def preprocess_image(image_path, save_preprocessed=False):
        """Legacy method - delegates to EnhancedEmotionDetectionService."""
        result = EnhancedEmotionDetectionService.analyze_image_with_preprocessing(
            image_path, save_preprocessed
        )
        
        # Convert to legacy format
        return {
            'success': result['success'],
            'preprocessed_image': None,  # Not used anymore
            'face_detected': result['face_detected'],
            'face_coordinates': result['face_coordinates'],
            'preprocessed_path': result['preprocessed_path'],
            'error': result['error']
        }
