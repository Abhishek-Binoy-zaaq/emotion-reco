from django.contrib import admin
from django.utils.html import format_html
from .models import SessionReport, CapturedFrame, Video, VideoCategory, PreprocessedImage


@admin.register(VideoCategory)
class VideoCategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'video_count', 'created_at']
    search_fields = ['name']
    readonly_fields = ['created_at']
    
    def video_count(self, obj):
        return obj.videos.count()
    video_count.short_description = 'Videos'


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'category', 'duration', 'uploaded_by', 'is_active', 'uploaded_at']
    list_filter = ['is_active', 'category', 'uploaded_at']
    search_fields = ['title', 'description']
    readonly_fields = ['uploaded_at']





class CapturedFrameInline(admin.TabularInline):
    model = CapturedFrame
    extra = 0
    readonly_fields = ['image_preview', 'timestamp', 'captured_at']
    fields = ['image_preview', 'timestamp']
    can_delete = False
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 50px; max-width: 100px;" />', obj.image.url)
        return "No image"
    image_preview.short_description = 'Preview'


@admin.register(SessionReport)
class SessionReportAdmin(admin.ModelAdmin):
    list_display = ['id', 'get_video_title', 'get_user_name', 'session_report', 'capture_count', 'is_completed', 'started_at']
    list_filter = ['is_completed', 'started_at', 'video']
    search_fields = ['video__title', 'user__username']
    readonly_fields = ['started_at', 'emotion_summary_display']
    inlines = [CapturedFrameInline]
    
    def get_video_title(self, obj):
        return obj.video.title if obj.video else 'N/A'
    get_video_title.short_description = 'Video'
    get_video_title.admin_order_field = 'video__title'
    
    def get_user_name(self, obj):
        return obj.user.username
    get_user_name.short_description = 'User'
    get_user_name.admin_order_field = 'user__username'
    
    def capture_count(self, obj):
        return obj.captures.count()
    capture_count.short_description = 'Captures'
    
    def emotion_summary_display(self, obj):
        summary = obj.get_emotion_summary()
        if not summary:
            return "No data"
        
        html = "<div style='font-family: monospace;'>"
        html += f"<p><strong>Total Captures:</strong> {summary.get('total_captures', 0)}</p>"
        html += f"<p><strong>Dominant Emotion:</strong> {summary.get('dominant_emotion', 'N/A')}</p>"
        html += "<p><strong>Distribution:</strong></p><ul>"
        
        for emotion, percentage in summary.get('percentages', {}).items():
            html += f"<li>{emotion}: {percentage:.1f}%</li>"
        
        html += "</ul></div>"
        return format_html(html)
    emotion_summary_display.short_description = 'Emotion Summary'


@admin.register(CapturedFrame)
class CapturedFrameAdmin(admin.ModelAdmin):
    list_display = ['id', 'session', 'image_preview', 'timestamp', 'captured_at']
    list_filter = ['captured_at', 'session']
    search_fields = ['session__video__title']
    readonly_fields = ['captured_at', 'image_preview']
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 100px; max-width: 200px;" />', obj.image.url)
        return "No image"
    image_preview.short_description = 'Preview'


@admin.register(PreprocessedImage)
class PreprocessedImageAdmin(admin.ModelAdmin):
    list_display = ['id', 'get_capture_id', 'image_preview', 'expression', 'expression_confidence', 'created_at']
    list_filter = ['expression', 'created_at']
    search_fields = ['expression']
    readonly_fields = ['created_at', 'image_preview', 'capture', 'expression', 'expression_confidence', 'all_expressions']
    
    def get_capture_id(self, obj):
        return f"Capture {obj.capture.id}"
    get_capture_id.short_description = 'Original Capture'
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 100px; max-width: 200px;" />', obj.image.url)
        return "No image"
    image_preview.short_description = 'Preview'

