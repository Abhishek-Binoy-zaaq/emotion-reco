"""
URL configuration for tutorials project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from rest_framework import routers

from quickstart import views

router = routers.DefaultRouter()
router.register(r"users", views.UserViewSet)
router.register(r"groups", views.GroupViewSet)
router.register(r"images", views.ImageUploadViewSet)
router.register(r"sessions", views.VideoSessionViewSet, basename='session')
router.register(r"captures", views.CapturedFrameViewSet)
router.register(r"videos", views.VideoViewSet)
router.register(r"categories", views.VideoCategoryViewSet)

# Wire up our API using automatic URL routing.
urlpatterns = [
    path("django-admin/", admin.site.urls),
    
    # Authentication
    path("", views.login_view, name="login"),
    path("signup/", views.signup_view, name="signup"),
    path("logout/", views.logout_view, name="logout"),
    
    # Admin URLs
    path("admin/", views.admin_dashboard, name="admin_dashboard"),
    path("admin/videos/", views.admin_videos, name="admin_videos"),
    path("admin/users/", views.admin_users, name="admin_users"),
    path("admin/reports/", views.admin_reports, name="admin_reports"),
    path("admin/video-report/<int:video_id>/", views.admin_video_report, name="admin_video_report"),
    
    # User URLs
    path("dashboard/", views.user_dashboard, name="user_dashboard"),
    path("my-sessions/", views.user_sessions, name="user_sessions"),
    path("session/<int:video_id>/", views.user_session, name="user_session"),
    path("report/<int:session_id>/", views.user_report, name="user_report"),
    
    # API
    path("api/", include(router.urls)),
    path("api-auth/", include("rest_framework.urls", namespace="rest_framework")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
