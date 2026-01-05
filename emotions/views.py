from django.contrib.auth.models import Group, User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils import timezone
from django.db.models import Count, Avg
from django.contrib import messages
from rest_framework import permissions, viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated, IsAdminUser

from .models import VideoSession, CapturedFrame, Video, VideoCategory, UserProfile
from .serializers import (
    GroupSerializer, UserSerializer,
    VideoSessionSerializer, VideoSessionCreateSerializer, 
    CapturedFrameSerializer, VideoSerializer, VideoCategorySerializer
)
from .services import EmotionDetectionService, SessionAnalyticsService


# Helper functions
def is_admin(user):
    return user.is_staff


# Authentication Views
@ensure_csrf_cookie
def signup_view(request):
    """User signup page"""
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect('admin_dashboard')
        return redirect('user_dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        
        # Validation
        if not username or not email or not password:
            messages.error(request, 'Username, email, and password are required.')
            return render(request, 'emotions/signup.html')
        
        if password != password_confirm:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'emotions/signup.html')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return render(request, 'emotions/signup.html')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered.')
            return render(request, 'emotions/signup.html')
        
        # Create user
        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name
            )
            
            # Auto-login after signup
            login(request, user)
            messages.success(request, f'Welcome {username}! Your account has been created successfully.')
            return redirect('user_dashboard')
            
        except Exception as e:
            messages.error(request, 'Error creating account. Please try again.')
            return render(request, 'emotions/signup.html')
    
    return render(request, 'emotions/signup.html')


@ensure_csrf_cookie
def login_view(request):
    """Login page"""
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect('admin_dashboard')
        return redirect('user_dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            if not user.is_active:
                return render(request, 'emotions/login.html', {'error': 'Your account has been disabled. Please contact admin.'})
            login(request, user)
            if user.is_staff:
                return redirect('admin_dashboard')
            return redirect('user_dashboard')
        else:
            return render(request, 'emotions/login.html', {'error': 'Invalid credentials'})
    
    return render(request, 'emotions/login.html')


def logout_view(request):
    """Logout"""
    logout(request)
    return redirect('login')


# Admin Views
@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    """Admin dashboard"""
    return render(request, 'emotions/admin_dashboard.html')


@login_required
@user_passes_test(is_admin)
def admin_videos(request):
    """Admin video management"""
    return render(request, 'emotions/admin_videos.html')


@login_required
@user_passes_test(is_admin)
def admin_users(request):
    """Admin user management"""
    return render(request, 'emotions/admin_users.html')


@login_required
@user_passes_test(is_admin)
def admin_reports(request):
    """Admin aggregate reports"""
    return render(request, 'emotions/admin_reports.html')


@login_required
@user_passes_test(is_admin)
def admin_video_report(request, video_id):
    """Admin per-video report"""
    return render(request, 'emotions/admin_video_report.html', {'video_id': video_id})


# User Views
@login_required
def user_dashboard(request):
    """User dashboard - video selection"""
    return render(request, 'emotions/user_dashboard.html')


@login_required
def user_sessions(request):
    """User's previous sessions"""
    return render(request, 'emotions/user_sessions.html')


@login_required
def user_session(request, video_id):
    """User video session"""
    return render(request, 'emotions/user_session.html', {'video_id': video_id})


@login_required
def user_report(request, session_id):
    """User session report"""
    return render(request, 'emotions/user_report.html', {'session_id': session_id})


# API ViewSets
class VideoCategoryViewSet(viewsets.ModelViewSet):
    """API endpoint for video categories"""
    queryset = VideoCategory.objects.all()
    serializer_class = VideoCategorySerializer
    permission_classes = [IsAuthenticated]
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return [IsAuthenticated()]


class VideoViewSet(viewsets.ModelViewSet):
    """API endpoint for videos"""
    queryset = Video.objects.filter(is_active=True)
    serializer_class = VideoSerializer
    parser_classes = [MultiPartParser, FormParser]
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return [IsAuthenticated()]
    
    def get_queryset(self):
        queryset = Video.objects.filter(is_active=True)
        category_id = self.request.query_params.get('category', None)
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(uploaded_by=self.request.user)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get video statistics"""
        videos = self.get_queryset()
        stats = []
        
        for video in videos:
            stats.append({
                'id': video.id,
                'title': video.title,
                'total_sessions': video.get_total_sessions(),
                'average_engagement': video.get_average_engagement()
            })
        
        return Response(stats)


class VideoSessionViewSet(viewsets.ModelViewSet):
    """API endpoint for video sessions"""
    serializer_class = VideoSessionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return VideoSession.objects.all()
        return VideoSession.objects.filter(user=self.request.user)
    
    def get_serializer_class(self):
        if self.action == 'create':
            return VideoSessionCreateSerializer
        return VideoSessionSerializer
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Mark a session as completed and generate report"""
        session = self.get_object()
        session.is_completed = True
        session.completed_at = timezone.now()
        
        # Generate and cache the report
        report_data = SessionAnalyticsService.generate_session_report(session)
        session.report_data = report_data
        session.save()
        
        return Response({'status': 'completed', 'report': report_data})
    
    @action(detail=True, methods=['get'])
    def report(self, request, pk=None):
        """Get comprehensive analytics report for a session"""
        session = self.get_object()
        
        # Use cached report if available, otherwise generate new one
        if session.report_data:
            return Response(session.report_data)
        
        # Generate report if not cached
        report_data = SessionAnalyticsService.generate_session_report(session)
        session.report_data = report_data
        session.save()
        
        return Response(report_data)
    
    @action(detail=False, methods=['get'])
    def aggregate_report(self, request):
        """Get aggregate report across all sessions (admin only)"""
        if not request.user.is_staff:
            return Response({'error': 'Admin access required'}, status=403)
        
        sessions = VideoSession.objects.filter(is_completed=True)
        
        total_sessions = sessions.count()
        total_users = User.objects.filter(is_staff=False).count()
        total_videos = Video.objects.filter(is_active=True).count()
        
        # Aggregate emotion data from cached reports
        all_emotion_counts = {}
        total_captures = 0
        
        for session in sessions:
            # Use cached report data if available
            if session.report_data:
                emotion_stats = session.report_data.get('emotion_stats', {})
                for emotion, stats in emotion_stats.items():
                    count = stats.get('count', 0)
                    all_emotion_counts[emotion] = all_emotion_counts.get(emotion, 0) + count
                    total_captures += count
            else:
                # Fallback to calculating from captures if no cached data
                summary = session.get_emotion_summary()
                for emotion, count in summary.get('counts', {}).items():
                    all_emotion_counts[emotion] = all_emotion_counts.get(emotion, 0) + count
                    total_captures += count
        
        # Calculate percentages
        emotion_percentages = {
            emotion: round((count / total_captures * 100), 2) if total_captures > 0 else 0
            for emotion, count in all_emotion_counts.items()
        }
        
        # Most popular videos
        popular_videos = Video.objects.annotate(
            session_count=Count('sessions')
        ).order_by('-session_count')[:5]
        
        popular_videos_data = [{
            'id': v.id,
            'title': v.title,
            'sessions': v.session_count,
            'engagement': v.get_average_engagement()
        } for v in popular_videos]
        
        # Most active users
        active_users = User.objects.filter(is_staff=False).annotate(
            session_count=Count('sessions')
        ).order_by('-session_count')[:5]
        
        active_users_data = [{
            'id': u.id,
            'username': u.username,
            'sessions': u.session_count
        } for u in active_users]
        
        return Response({
            'total_sessions': total_sessions,
            'total_users': total_users,
            'total_videos': total_videos,
            'total_captures': total_captures,
            'emotion_distribution': emotion_percentages,
            'emotion_counts': all_emotion_counts,
            'popular_videos': popular_videos_data,
            'active_users': active_users_data
        })


class CapturedFrameViewSet(viewsets.ModelViewSet):
    """API endpoint for captured frames"""
    queryset = CapturedFrame.objects.all()
    serializer_class = CapturedFrameSerializer
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [IsAuthenticated]
    
    def create(self, request, *args, **kwargs):
        """Create a new captured frame and analyze it"""
        from .models import PreprocessedImage
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        
        # Analyze the captured frame (and save cropped face if found)
        analysis_result = EmotionDetectionService.analyze_image(
            instance.image.path,
            save_preprocessed=True
        )
        
        if analysis_result['success']:
            # Save preprocessed image to separate model if it was generated
            preprocessed_path = analysis_result.get('preprocessed_path')
            if preprocessed_path:
                try:
                    # Create PreprocessedImage instance
                    # We need to get the relative path for ImageField
                    # ImagePreprocessor returns full path
                    import os
                    from django.conf import settings
                    
                    rel_path = os.path.relpath(preprocessed_path, settings.MEDIA_ROOT)
                    
                    PreprocessedImage.objects.create(
                        capture=instance,
                        image=rel_path,
                        expression=analysis_result['expression'],
                        expression_confidence=analysis_result['confidence'],
                        all_expressions=analysis_result['all_emotions']
                    )
                    print(f"[OK] Saved preprocessed image to model with emotion data: {rel_path}", flush=True)
                except Exception as e:
                    print(f"[FAIL] Failed to save preprocessed image model: {e}", flush=True)
        
        # We return the captured frame data. The frontend might need to fetch the preprocessed image separately or we can include it.
        # For now, following the pattern of returning the captured frame serializer.
        return Response(self.get_serializer(instance).data, status=status.HTTP_201_CREATED)


class UserViewSet(viewsets.ModelViewSet):
    """API endpoint for user management"""
    queryset = User.objects.filter(is_staff=False)
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]
    
    def create(self, request, *args, **kwargs):
        """Create a new user"""
        username = request.data.get('username')
        password = request.data.get('password')
        email = request.data.get('email', '')
        first_name = request.data.get('first_name', '')
        last_name = request.data.get('last_name', '')
        
        if not username or not password:
            return Response({'error': 'Username and password are required'}, status=400)
        
        if User.objects.filter(username=username).exists():
            return Response({'error': 'Username already exists'}, status=400)
        
        user = User.objects.create_user(
            username=username,
            password=password,
            email=email,
            first_name=first_name,
            last_name=last_name
        )
        
        serializer = self.get_serializer(user)
        return Response(serializer.data, status=201)





class GroupViewSet(viewsets.ModelViewSet):
    """API endpoint that allows groups to be viewed or edited"""
    queryset = Group.objects.all().order_by("name")
    serializer_class = GroupSerializer
    permission_classes = [IsAdminUser]
