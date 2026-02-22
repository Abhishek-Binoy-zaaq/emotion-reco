from django.apps import AppConfig
import os


class EmotionsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'emotions'
    
    def ready(self):
        """
        Called when Django app is ready.
        Optionally pre-load emotion detection models to avoid cold-start delay.
        Set WARMUP_MODELS=1 environment variable to enable.
        """
        if os.environ.get('WARMUP_MODELS') == '1':
            # Only warmup in the main process, not in the autoreloader
            import sys
            if 'runserver' not in sys.argv or os.environ.get('RUN_MAIN') == 'true':
                try:
                    from .image_preprocessing import warmup_models
                    warmup_models()
                except Exception as e:
                    print(f"[WARMUP] Skipped: {e}")
