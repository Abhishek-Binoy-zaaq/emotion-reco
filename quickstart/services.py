"""
Service layer for emotion detection and analysis
"""
from deepface import DeepFace
import sys


class EmotionDetectionService:
    """Handles facial emotion detection"""
    
    BACKENDS = ['opencv', 'ssd', 'retinaface']
    
    @staticmethod
    def analyze_image(image_path):
        """
        Analyze an image for facial expressions
        
        Args:
            image_path: Path to the image file
            
        Returns:
            dict: {
                'success': bool,
                'expression': str,
                'confidence': float,
                'all_emotions': dict,
                'error': str (if failed)
            }
        """
        print(f"\n=== ANALYZING IMAGE: {image_path} ===", flush=True)
        sys.stdout.flush()
        
        result_data = {
            'success': False,
            'expression': None,
            'confidence': None,
            'all_emotions': None,
            'error': None
        }
        
        try:
            result = None
            last_error = None
            
            # Try different backends
            for backend in EmotionDetectionService.BACKENDS:
                try:
                    print(f"Trying backend: {backend}", flush=True)
                    sys.stdout.flush()
                    
                    result = DeepFace.analyze(
                        img_path=image_path,
                        actions=['emotion'],
                        enforce_detection=False,
                        detector_backend=backend,
                        silent=True
                    )
                    
                    print(f"✓ Success with backend: {backend}", flush=True)
                    sys.stdout.flush()
                    break
                    
                except Exception as e:
                    last_error = str(e)
                    print(f"✗ Backend {backend} failed: {e}", flush=True)
                    sys.stdout.flush()
                    continue
            
            if result is None:
                raise Exception(f"All backends failed. Last error: {last_error}")
            
            # Extract results
            if isinstance(result, list):
                result = result[0]
            
            emotions = result.get('emotion', {})
            dominant_emotion = result.get('dominant_emotion', 'unknown')
            
            print(f"🎭 Detected emotion: {dominant_emotion}", flush=True)
            print(f"📊 All emotions: {emotions}", flush=True)
            sys.stdout.flush()
            
            # Convert numpy types to Python native types
            emotions_serializable = {k: float(v) for k, v in emotions.items()}
            
            if emotions and dominant_emotion != 'unknown':
                result_data['success'] = True
                result_data['expression'] = dominant_emotion
                result_data['confidence'] = float(emotions.get(dominant_emotion, 0))
                result_data['all_emotions'] = emotions_serializable
                print(f"✓ Analysis complete: {dominant_emotion}", flush=True)
            else:
                result_data['error'] = 'No face detected in image'
                print(f"✗ No face detected", flush=True)
            
            sys.stdout.flush()
            
        except Exception as e:
            error_msg = str(e)
            print(f"\n❌ ERROR in face detection: {error_msg}", flush=True)
            sys.stdout.flush()
            result_data['error'] = error_msg
        
        return result_data


class SessionAnalyticsService:
    """Handles session analytics and reporting"""
    
    @staticmethod
    def generate_session_report(session):
        """
        Generate a comprehensive report for a video session
        
        Args:
            session: VideoSession instance
            
        Returns:
            dict: Comprehensive session analytics
        """
        captures = session.captures.all()
        
        # Basic stats
        total_captures = captures.count()
        successful_detections = captures.exclude(
            expression__in=['error', 'no_face_detected', None]
        ).count()
        
        # Emotion timeline
        emotion_timeline = []
        for capture in captures:
            emotion_timeline.append({
                'timestamp': capture.timestamp,
                'expression': capture.expression,
                'confidence': capture.expression_confidence
            })
        
        # Emotion distribution
        emotion_counts = {}
        emotion_confidences = {}
        
        for capture in captures:
            if capture.expression and capture.expression not in ['error', 'no_face_detected']:
                emotion_counts[capture.expression] = emotion_counts.get(capture.expression, 0) + 1
                
                if capture.expression not in emotion_confidences:
                    emotion_confidences[capture.expression] = []
                emotion_confidences[capture.expression].append(capture.expression_confidence)
        
        # Calculate percentages and average confidence
        emotion_stats = {}
        for emotion, count in emotion_counts.items():
            percentage = (count / successful_detections * 100) if successful_detections > 0 else 0
            avg_confidence = sum(emotion_confidences[emotion]) / len(emotion_confidences[emotion])
            
            emotion_stats[emotion] = {
                'count': count,
                'percentage': round(percentage, 2),
                'avg_confidence': round(avg_confidence, 2)
            }
        
        # Dominant emotion
        dominant_emotion = max(emotion_counts.items(), key=lambda x: x[1])[0] if emotion_counts else None
        
        # Engagement score (based on non-neutral emotions)
        non_neutral_count = sum(count for emotion, count in emotion_counts.items() if emotion != 'neutral')
        engagement_score = (non_neutral_count / successful_detections * 100) if successful_detections > 0 else 0
        
        return {
            'session_id': session.id,
            'video_name': session.video.title if session.video else 'Unknown Video',
            'video_duration': session.video.duration if session.video else 0,
            'started_at': session.started_at.isoformat(),
            'completed_at': session.completed_at.isoformat() if session.completed_at else None,
            'total_captures': total_captures,
            'successful_detections': successful_detections,
            'detection_rate': round((successful_detections / total_captures * 100), 2) if total_captures > 0 else 0,
            'dominant_emotion': dominant_emotion,
            'emotion_stats': emotion_stats,
            'emotion_timeline': emotion_timeline,
            'engagement_score': round(engagement_score, 2)
        }
