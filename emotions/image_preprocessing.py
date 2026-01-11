"""
Image Preprocessing Pipeline for Emotion Detection
Handles: Face Detection → Face Cropping → Emotion Detection
"""
import cv2
import numpy as np
from pathlib import Path
import sys
from deepface import DeepFace


class ImagePreprocessor:
    """Handles image preprocessing before emotion detection"""
    
    # Face detection backends in order of preference
    FACE_DETECTORS = ['opencv', 'ssd', 'retinaface', 'mtcnn']
    
    # Minimum face size (width, height) in pixels
    MIN_FACE_SIZE = (48, 48)
    
    # Padding around detected face (percentage)
    FACE_PADDING = 0.2
    
    @staticmethod
    def preprocess_image(image_path, save_preprocessed=False):
        """
        Complete preprocessing pipeline:
        1. Load image
        2. Detect face
        3. Crop face with padding
        4. Return preprocessed image
        
        Args:
            image_path: Path to the input image
            save_preprocessed: Whether to save the preprocessed image
            
        Returns:
            dict: {
                'success': bool,
                'preprocessed_image': numpy array or None,
                'face_detected': bool,
                'face_coordinates': dict or None,
                'preprocessed_path': str or None,
                'error': str or None
            }
        """
        print(f"\n=== PREPROCESSING IMAGE: {image_path} ===", flush=True)
        sys.stdout.flush()
        
        result = {
            'success': False,
            'preprocessed_image': None,
            'face_detected': False,
            'face_coordinates': None,
            'preprocessed_path': None,
            'error': None
        }
        
        try:
            # Step 1: Load image
            image = cv2.imread(str(image_path))
            if image is None:
                raise ValueError(f"Could not load image from {image_path}")
            
            print(f"[OK] Image loaded: {image.shape}", flush=True)
            sys.stdout.flush()
            
            # Step 2: Detect face
            face_data = ImagePreprocessor.detect_face(image)
            
            if not face_data['face_detected']:
                result['error'] = 'No face detected in image'
                print(f"[FAIL] No face detected", flush=True)
                sys.stdout.flush()
                return result
            
            result['face_detected'] = True
            result['face_coordinates'] = face_data['coordinates']
            
            print(f"[OK] Face detected at: {face_data['coordinates']}", flush=True)
            sys.stdout.flush()
            
            # Step 3: Crop face with padding
            cropped_face = ImagePreprocessor.crop_face(
                image, 
                face_data['coordinates']
            )
            
            if cropped_face is None:
                result['error'] = 'Failed to crop face'
                print(f"[FAIL] Failed to crop face", flush=True)
                sys.stdout.flush()
                return result
            
            print(f"[OK] Face cropped: {cropped_face.shape}", flush=True)
            sys.stdout.flush()
            
            # Step 4: Validate face size
            if not ImagePreprocessor.validate_face_size(cropped_face):
                result['error'] = f'Face too small (minimum {ImagePreprocessor.MIN_FACE_SIZE})'
                print(f"[FAIL] Face too small", flush=True)
                sys.stdout.flush()
                return result
            
            result['preprocessed_image'] = cropped_face
            result['success'] = True
            
            # Step 5: Save preprocessed image if requested
            if save_preprocessed:
                preprocessed_path = ImagePreprocessor.save_preprocessed_image(
                    cropped_face, 
                    image_path
                )
                result['preprocessed_path'] = preprocessed_path
                print(f"[OK] Preprocessed image saved: {preprocessed_path}", flush=True)
                sys.stdout.flush()
            
            print(f"[OK] Preprocessing complete", flush=True)
            sys.stdout.flush()
            
        except Exception as e:
            error_msg = str(e)
            print(f"[ERROR] Preprocessing error: {error_msg}", flush=True)
            sys.stdout.flush()
            result['error'] = error_msg
        
        return result
    
    @staticmethod
    def detect_face(image):
        """
        Detect face in image using multiple backends
        
        Args:
            image: numpy array (BGR format from cv2)
            
        Returns:
            dict: {
                'face_detected': bool,
                'coordinates': dict or None,
                'backend_used': str or None
            }
        """
        result = {
            'face_detected': False,
            'coordinates': None,
            'backend_used': None
        }
        
        # Try OpenCV Haar Cascade first (fastest)
        try:
            face_cascade = cv2.CascadeClassifier(
                cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            )
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(
                gray, 
                scaleFactor=1.1, 
                minNeighbors=5, 
                minSize=ImagePreprocessor.MIN_FACE_SIZE
            )
            
            if len(faces) > 0:
                # Get the largest face
                largest_face = max(faces, key=lambda f: f[2] * f[3])
                x, y, w, h = largest_face
                
                result['face_detected'] = True
                result['coordinates'] = {
                    'x': int(x),
                    'y': int(y),
                    'width': int(w),
                    'height': int(h)
                }
                result['backend_used'] = 'opencv_haar'
                
                print(f"[OK] Face detected with OpenCV Haar Cascade", flush=True)
                sys.stdout.flush()
                return result
        
        except Exception as e:
            print(f"OpenCV Haar Cascade failed: {e}", flush=True)
            sys.stdout.flush()
        
        # Try DeepFace backends if OpenCV fails
        for backend in ImagePreprocessor.FACE_DETECTORS:
            try:
                print(f"Trying DeepFace backend: {backend}", flush=True)
                sys.stdout.flush()
                
                # Use DeepFace to detect face
                face_objs = DeepFace.extract_faces(
                    img_path=image,
                    detector_backend=backend,
                    enforce_detection=True,
                    align=True
                )
                
                if face_objs and len(face_objs) > 0:
                    # Get the first face
                    face_obj = face_objs[0]
                    facial_area = face_obj.get('facial_area', {})
                    
                    result['face_detected'] = True
                    result['coordinates'] = {
                        'x': facial_area.get('x', 0),
                        'y': facial_area.get('y', 0),
                        'width': facial_area.get('w', 0),
                        'height': facial_area.get('h', 0)
                    }
                    result['backend_used'] = backend
                    
                    print(f"[OK] Face detected with {backend}", flush=True)
                    sys.stdout.flush()
                    return result
            
            except Exception as e:
                print(f"Backend {backend} failed: {e}", flush=True)
                sys.stdout.flush()
                continue
        
        print(f"[FAIL] No face detected with any backend", flush=True)
        sys.stdout.flush()
        return result
    
    @staticmethod
    def crop_face(image, coordinates):
        """
        Crop face from image with padding
        
        Args:
            image: numpy array (BGR format)
            coordinates: dict with x, y, width, height
            
        Returns:
            numpy array: Cropped face image or None
        """
        try:
            x = coordinates['x']
            y = coordinates['y']
            w = coordinates['width']
            h = coordinates['height']
            
            # Add padding
            padding_w = int(w * ImagePreprocessor.FACE_PADDING)
            padding_h = int(h * ImagePreprocessor.FACE_PADDING)
            
            # Calculate crop coordinates with padding
            x1 = max(0, x - padding_w)
            y1 = max(0, y - padding_h)
            x2 = min(image.shape[1], x + w + padding_w)
            y2 = min(image.shape[0], y + h + padding_h)
            
            # Crop the face
            cropped_face = image[y1:y2, x1:x2]
            
            return cropped_face
        
        except Exception as e:
            print(f"Error cropping face: {e}", flush=True)
            sys.stdout.flush()
            return None
    
    @staticmethod
    def validate_face_size(face_image):
        """
        Check if face meets minimum size requirements
        
        Args:
            face_image: numpy array
            
        Returns:
            bool: True if face is large enough
        """
        if face_image is None:
            return False
        
        height, width = face_image.shape[:2]
        min_width, min_height = ImagePreprocessor.MIN_FACE_SIZE
        
        return width >= min_width and height >= min_height
    
    @staticmethod
    def save_preprocessed_image(image, original_path):
        """
        Save preprocessed image
        
        Args:
            image: numpy array
            original_path: Path to original image
            
        Returns:
            str: Path to saved preprocessed image
        """
        try:
            original_path = Path(original_path)
            preprocessed_path = original_path.parent / f"{original_path.stem}_preprocessed{original_path.suffix}"
            
            cv2.imwrite(str(preprocessed_path), image)
            
            return str(preprocessed_path)
        
        except Exception as e:
            print(f"Error saving preprocessed image: {e}", flush=True)
            sys.stdout.flush()
            return None


class EnhancedEmotionDetectionService:
    """Enhanced emotion detection with preprocessing pipeline"""
    
    @staticmethod
    def analyze_image_with_preprocessing(image_path, save_preprocessed=False):
        """
        Complete pipeline: Preprocess → Detect Emotion
        
        Args:
            image_path: Path to the input image
            save_preprocessed: Whether to save preprocessed images
            
        Returns:
            dict: {
                'success': bool,
                'face_detected': bool,
                'face_coordinates': dict or None,
                'expression': str or None,
                'confidence': float or None,
                'all_emotions': dict or None,
                'preprocessed_path': str or None,
                'error': str or None
            }
        """
        print(f"\n=== ENHANCED EMOTION DETECTION ===", flush=True)
        print(f"Image: {image_path}", flush=True)
        sys.stdout.flush()
        
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
        
        try:
            # Step 1: Preprocess image
            preprocess_result = ImagePreprocessor.preprocess_image(
                image_path, 
                save_preprocessed=save_preprocessed
            )
            
            if not preprocess_result['success']:
                result['error'] = preprocess_result['error']
                result['face_detected'] = preprocess_result['face_detected']
                print(f"[FAIL] Preprocessing failed: {result['error']}", flush=True)
                sys.stdout.flush()
                return result
            
            result['face_detected'] = True
            result['face_coordinates'] = preprocess_result['face_coordinates']
            result['preprocessed_path'] = preprocess_result.get('preprocessed_path')
            
            # Step 2: Detect emotion on preprocessed image
            preprocessed_image = preprocess_result['preprocessed_image']
            
            print(f"Detecting emotion on preprocessed image...", flush=True)
            sys.stdout.flush()
            
            emotion_result = EnhancedEmotionDetectionService.detect_emotion(
                preprocessed_image
            )
            
            if not emotion_result['success']:
                result['error'] = emotion_result['error']
                print(f"[FAIL] Emotion detection failed: {result['error']}", flush=True)
                sys.stdout.flush()
                return result
            
            # Combine results
            result['success'] = True
            result['expression'] = emotion_result['expression']
            result['confidence'] = emotion_result['confidence']
            result['all_emotions'] = emotion_result['all_emotions']
            
            print(f"[OK] Complete! Emotion: {result['expression']} ({result['confidence']:.2f}%)", flush=True)
            sys.stdout.flush()
            
        except Exception as e:
            error_msg = str(e)
            print(f"[ERROR] Error in enhanced emotion detection: {error_msg}", flush=True)
            sys.stdout.flush()
            result['error'] = error_msg
        
        return result

    
    @staticmethod
    def crop_face(image, coordinates):
        """
        Crop face from image with padding
        
        Args:
            image: numpy array (BGR format)
            coordinates: dict with x, y, width, height
            
        Returns:
            numpy array: Cropped face image or None
        """
        try:
            x = coordinates['x']
            y = coordinates['y']
            w = coordinates['width']
            h = coordinates['height']
            
            # Add padding
            padding_w = int(w * ImagePreprocessor.FACE_PADDING)
            padding_h = int(h * ImagePreprocessor.FACE_PADDING)
            
            # Calculate crop coordinates with padding
            x1 = max(0, x - padding_w)
            y1 = max(0, y - padding_h)
            x2 = min(image.shape[1], x + w + padding_w)
            y2 = min(image.shape[0], y + h + padding_h)
            
            # Crop the face
            cropped_face = image[y1:y2, x1:x2]
            
            return cropped_face
        
        except Exception as e:
            print(f"Error cropping face: {e}", flush=True)
            sys.stdout.flush()
            return None
    
    @staticmethod
    def validate_face_size(face_image):
        """
        Check if face meets minimum size requirements
        
        Args:
            face_image: numpy array
            
        Returns:
            bool: True if face is large enough
        """
        if face_image is None:
            return False
        
        height, width = face_image.shape[:2]
        min_width, min_height = ImagePreprocessor.MIN_FACE_SIZE
        
        return width >= min_width and height >= min_height
    
    @staticmethod
    def save_preprocessed_image(image, original_path):
        """
        Save preprocessed image
        
        Args:
            image: numpy array
            original_path: Path to original image
            
        Returns:
            str: Path to saved preprocessed image
        """
        try:
            original_path = Path(original_path)
            preprocessed_path = original_path.parent / f"{original_path.stem}_preprocessed{original_path.suffix}"
            
            cv2.imwrite(str(preprocessed_path), image)
            
            return str(preprocessed_path)
        
        except Exception as e:
            print(f"Error saving preprocessed image: {e}", flush=True)
            sys.stdout.flush()
            return None


class EnhancedEmotionDetectionService:
    """Enhanced emotion detection with preprocessing pipeline"""
    
    @staticmethod
    def analyze_image_with_preprocessing(image_path, save_preprocessed=False):
        """
        Complete pipeline: Preprocess → Detect Emotion
        
        Args:
            image_path: Path to the input image
            save_preprocessed: Whether to save preprocessed images
            
        Returns:
            dict: {
                'success': bool,
                'face_detected': bool,
                'face_coordinates': dict or None,
                'expression': str or None,
                'confidence': float or None,
                'all_emotions': dict or None,
                'preprocessed_path': str or None,
                'error': str or None
            }
        """
        print(f"\n=== ENHANCED EMOTION DETECTION ===", flush=True)
        print(f"Image: {image_path}", flush=True)
        sys.stdout.flush()
        
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
        
        try:
            # Step 1: Preprocess image
            preprocess_result = ImagePreprocessor.preprocess_image(
                image_path, 
                save_preprocessed=save_preprocessed
            )
            
            if not preprocess_result['success']:
                result['error'] = preprocess_result['error']
                result['face_detected'] = preprocess_result['face_detected']
                print(f"✗ Preprocessing failed: {result['error']}", flush=True)
                sys.stdout.flush()
                return result
            
            result['face_detected'] = True
            result['face_coordinates'] = preprocess_result['face_coordinates']
            result['preprocessed_path'] = preprocess_result.get('preprocessed_path')
            
            # Step 2: Detect emotion on preprocessed image
            preprocessed_image = preprocess_result['preprocessed_image']
            
            print(f"Detecting emotion on preprocessed image...", flush=True)
            sys.stdout.flush()
            
            emotion_result = EnhancedEmotionDetectionService.detect_emotion(
                preprocessed_image
            )
            
            if not emotion_result['success']:
                result['error'] = emotion_result['error']
                print(f"✗ Emotion detection failed: {result['error']}", flush=True)
                sys.stdout.flush()
                return result
            
            # Combine results
            result['success'] = True
            result['expression'] = emotion_result['expression']
            result['confidence'] = emotion_result['confidence']
            result['all_emotions'] = emotion_result['all_emotions']
            
            print(f"✓ Complete! Emotion: {result['expression']} ({result['confidence']:.2f}%)", flush=True)
            sys.stdout.flush()
            
        except Exception as e:
            error_msg = str(e)
            print(f"❌ Error in enhanced emotion detection: {error_msg}", flush=True)
            sys.stdout.flush()
            result['error'] = error_msg
        
        return result
    
    @staticmethod
    def detect_emotion(image):
        """
        Detect emotion from preprocessed face image
        """
        # Placeholder or remove if not used
        print("Warning: detect_emotion not implemented", flush=True)
        return {'success': False, 'error': 'Not implemented'}