from django.conf import settings
from django import db
import os
import time


def process_captured_frame_task(capture_id):
    """
    Process a captured frame using DeepFace.
    Called in a background thread so the web request returns immediately.
    """
    try:
        from emotions.models import CapturedFrame, PreprocessedImage
        from emotions.image_preprocessing import EnhancedEmotionDetectionService
        
        # Small delay to ensure the DB transaction from the view has committed
        time.sleep(0.3)

        # Close any stale DB connections inherited from the parent thread
        db.close_old_connections()

        try:
            instance = CapturedFrame.objects.get(id=capture_id)
        except CapturedFrame.DoesNotExist:
            print(f"[FAIL] Capture {capture_id} not found in DB.", flush=True)
            return False

        # Skip if already processed
        if hasattr(instance, 'preprocessed_version'):
            try:
                instance.preprocessed_version
                print(f"[SKIP] Capture {capture_id} already processed.", flush=True)
                return True
            except Exception:
                pass

        # Analyze the image - this now uses the fast opencv detector
        analysis_result = EnhancedEmotionDetectionService.analyze_image_with_preprocessing(
            instance.image.path,
            save_preprocessed=True
        )

        if analysis_result['success']:
            preprocessed_path = analysis_result.get('preprocessed_path')
            rel_path = None
            if preprocessed_path:
                rel_path = os.path.relpath(preprocessed_path, settings.MEDIA_ROOT)
            
            PreprocessedImage.objects.create(
                captured_frame=instance,
                image=rel_path or '',
                expression=analysis_result['expression'],
                expression_confidence=analysis_result['confidence'],
                all_expressions=analysis_result['all_emotions'],
                session=instance.session,
                user=instance.session.user,
                video=instance.session.video
            )
            print(f"[OK] Capture {capture_id}: {analysis_result['expression']} ({analysis_result['confidence']:.1f}%)", flush=True)
        else:
            print(f"[FAIL] Capture {capture_id}: {analysis_result.get('error')}", flush=True)
             
        return True
    except Exception as e:
        print(f"[ERROR] Task failed for capture {capture_id}: {str(e)}", flush=True)
        return False
    finally:
        db.close_old_connections()
