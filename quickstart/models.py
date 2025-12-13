from django.db import models
from django.contrib.auth.models import User
import json


class UserProfile(models.Model):
    """Extended user profile for approval system"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    is_approved = models.BooleanField(default=False, help_text="Admin approval status")
    signup_date = models.DateTimeField(auto_now_add=True)
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_users')
    approved_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.user.username} - {'Approved' if self.is_approved else 'Pending'}"


class VideoCategory(models.Model):
    """Categories for organizing videos"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Video Categories"
        ordering = ['name']


class Video(models.Model):
    """Videos uploaded by admin"""
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    category = models.ForeignKey(VideoCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='videos')
    video_file = models.FileField(upload_to='videos/')
    duration = models.IntegerField(help_text="Duration in seconds")
    thumbnail = models.ImageField(upload_to='thumbnails/', blank=True, null=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='uploaded_videos')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.title
    
    def get_total_sessions(self):
        return self.sessions.count()
    
    def get_average_engagement(self):
        sessions = self.sessions.filter(is_completed=True)
        if not sessions:
            return 0
        
        total_engagement = 0
        for session in sessions:
            summary = session.get_emotion_summary()
            emotion_counts = summary.get('counts', {})
            total_captures = summary.get('total_captures', 0)
            
            if total_captures > 0:
                non_neutral = sum(count for emotion, count in emotion_counts.items() if emotion != 'neutral')
                engagement = (non_neutral / total_captures * 100)
                total_engagement += engagement
        
        return round(total_engagement / sessions.count(), 2) if sessions.count() > 0 else 0
    
    class Meta:
        ordering = ['-uploaded_at']


class VideoSession(models.Model):
    """Represents a video viewing session"""
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name='sessions', null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sessions')
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    is_completed = models.BooleanField(default=False)
    
    # Cached report data (stored as JSON)
    report_data = models.JSONField(null=True, blank=True, help_text="Cached session report")
    
    def __str__(self):
        return f"Session {self.id} - {self.user.username} - {self.video.title if self.video else 'Unknown'}"
    
    def get_emotion_summary(self):
        """Calculate emotion statistics for this session"""
        captures = self.captures.all()
        if not captures:
            return {}
        
        emotion_counts = {}
        total_captures = 0
        
        for capture in captures:
            if capture.expression and capture.expression not in ['error', 'no_face_detected']:
                emotion_counts[capture.expression] = emotion_counts.get(capture.expression, 0) + 1
                total_captures += 1
        
        # Calculate percentages
        emotion_percentages = {
            emotion: (count / total_captures * 100) if total_captures > 0 else 0
            for emotion, count in emotion_counts.items()
        }
        
        return {
            'counts': emotion_counts,
            'percentages': emotion_percentages,
            'total_captures': total_captures,
            'dominant_emotion': max(emotion_counts.items(), key=lambda x: x[1])[0] if emotion_counts else None
        }
    
    class Meta:
        ordering = ['-started_at']


class CapturedFrame(models.Model):
    """Represents a single captured frame during video playback"""
    session = models.ForeignKey(VideoSession, on_delete=models.CASCADE, related_name='captures')
    image = models.ImageField(upload_to='captures/')
    timestamp = models.FloatField(help_text="Video timestamp in seconds")
    captured_at = models.DateTimeField(auto_now_add=True)
    
    # Expression analysis results
    expression = models.CharField(max_length=50, blank=True, null=True)
    expression_confidence = models.FloatField(blank=True, null=True)
    all_expressions = models.JSONField(blank=True, null=True)
    
    def __str__(self):
        return f"Frame at {self.timestamp}s - {self.expression or 'pending'}"
    
    class Meta:
        ordering = ['timestamp']


class PreprocessedImage(models.Model):
    """Represents the preprocessed (cropped) face from a captured frame"""
    capture = models.OneToOneField(CapturedFrame, on_delete=models.CASCADE, related_name='preprocessed_version')
    image = models.ImageField(upload_to='preprocessed/')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Preprocessed frame {self.capture.id}"



class UploadedImage(models.Model):
    """Legacy model for single image uploads"""
    image = models.ImageField(upload_to='uploads/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    expression = models.CharField(max_length=50, blank=True, null=True)
    expression_confidence = models.FloatField(blank=True, null=True)
    all_expressions = models.JSONField(blank=True, null=True)
    
    def __str__(self):
        return f"Image {self.id} - {self.image.name}"
    
    class Meta:
        ordering = ['-uploaded_at']
