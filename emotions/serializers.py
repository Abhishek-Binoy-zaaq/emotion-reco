from django.contrib.auth.models import Group, User
from rest_framework import serializers
from .models import SessionReport, CapturedFrame, Video, VideoCategory, PreprocessedImage


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name", "is_staff", "is_active"]


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ["url", "name"]


class VideoCategorySerializer(serializers.ModelSerializer):
    video_count = serializers.SerializerMethodField()
    
    class Meta:
        model = VideoCategory
        fields = ["id", "name", "description", "created_at", "video_count"]
        read_only_fields = ["id", "created_at"]
    
    def get_video_count(self, obj):
        return obj.videos.filter(is_active=True).count()


class VideoSerializer(serializers.ModelSerializer):
    uploaded_by_name = serializers.CharField(source='uploaded_by.username', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    total_sessions = serializers.SerializerMethodField()
    average_engagement = serializers.SerializerMethodField()
    
    class Meta:
        model = Video
        fields = ["id", "title", "description", "category", "category_name", "video_file", 
                  "duration", "thumbnail", "uploaded_by", "uploaded_by_name", "uploaded_at", 
                  "is_active", "total_sessions", "average_engagement"]
        read_only_fields = ["id", "uploaded_at", "uploaded_by"]
    
    def get_total_sessions(self, obj):
        return obj.get_total_sessions()
    
    def get_average_engagement(self, obj):
        return obj.get_average_engagement()





class CapturedFrameSerializer(serializers.ModelSerializer):
    class Meta:
        model = CapturedFrame
        fields = ["id", "session", "image", "timestamp", "captured_at"]
        read_only_fields = ["id", "captured_at"]


class PreprocessedImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PreprocessedImage
        fields = ["id", "capture", "image", "created_at", "expression", "expression_confidence", "all_expressions"]
        read_only_fields = ["id", "created_at"]


class SessionReportSerializer(serializers.ModelSerializer):
    captures = CapturedFrameSerializer(many=True, read_only=True)
    emotion_summary = serializers.SerializerMethodField()
    video_title = serializers.CharField(source='video.title', read_only=True)
    user_name = serializers.CharField(source='user.username', read_only=True)
    session_id = serializers.IntegerField(source='id', read_only=True)
    video_id = serializers.IntegerField(source='video.id', read_only=True)
    
    class Meta:
        model = SessionReport
        fields = ["session_id", "video_id", "video_title", "user", "user_name", "started_at", 
                  "completed_at", "is_completed", "captures", "emotion_summary", "session_report"]
        read_only_fields = ["session_id", "started_at", "user", "video_id", "session_report"]
    
    def get_emotion_summary(self, obj):
        return obj.get_emotion_summary()


class SessionReportCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SessionReport
        fields = ["id", "video"]
        read_only_fields = ["id"]
