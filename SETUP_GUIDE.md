# Quick Setup Guide

## Step-by-Step Setup

### 1. Install Dependencies
```bash
pip install django djangorestframework pillow deepface opencv-python tensorflow tf-keras
```

### 2. Database Setup
```bash
python manage.py makemigrations
python manage.py migrate
```

### 3. Create Demo Users
```bash
python manage.py shell < create_demo_users.py
```

### 4. Start Server
```bash
python manage.py runserver
```

### 5. Login
Go to http://127.0.0.1:8000/

## Demo Accounts

### Admin Account
- **Username**: admin
- **Password**: admin123
- **Capabilities**:
  - Upload and manage videos
  - View all users
  - Access aggregate reports
  - Full system control

### User Account
- **Username**: user
- **Password**: user123
- **Capabilities**:
  - Browse video library
  - Record emotion sessions
  - View personal reports

## First Steps

### As Admin:
1. Login with admin/admin123
2. Go to "Manage Videos"
3. Upload a video (MP4, max 60 seconds recommended)
4. Video is now available for all users

### As User:
1. Login with user/user123
2. Select a video from the library
3. Click "Start Session"
4. Allow webcam access
5. Watch the video (your emotions are captured automatically)
6. Click "View Report" when done

## Troubleshooting

### Webcam not working
- Check browser permissions
- Ensure no other app is using webcam
- Try refreshing the page

### Emotion detection not working
- Wait for models to download on first run (takes 1-2 minutes)
- Ensure good lighting
- Face the camera directly

### Video upload fails
- Check file size (keep under 100MB)
- Use MP4 format
- Ensure video duration is set correctly

## File Structure

```
quickstart/
├── models.py              # Database models
├── views.py               # Views and API endpoints
├── serializers.py         # API serializers
├── services.py            # Business logic
├── admin.py               # Django admin config
├── templates/
│   └── quickstart/
│       ├── login.html              # Login page
│       ├── admin_dashboard.html    # Admin home
│       ├── admin_videos.html       # Video management
│       ├── admin_users.html        # User management
│       ├── admin_reports.html      # Aggregate reports
│       ├── user_dashboard.html     # User video library
│       ├── user_session.html       # Video session
│       └── user_report.html        # Session report
└── static/
    └── quickstart/
        ├── css/
        │   └── admin-common.css    # Shared styles
        └── js/
            ├── admin-videos.js     # Video management logic
            └── video-session.js    # Session management

tutorials/
└── urls.py                # URL routing
```

## URLs

### Authentication
- `/` - Login page
- `/logout/` - Logout

### Admin URLs
- `/admin/` - Admin dashboard
- `/admin/videos/` - Video management
- `/admin/users/` - User management
- `/admin/reports/` - Aggregate reports

### User URLs
- `/dashboard/` - Video library
- `/session/<video_id>/` - Video session
- `/report/<session_id>/` - Session report

### API Endpoints
- `/api/videos/` - Video CRUD
- `/api/sessions/` - Session CRUD
- `/api/captures/` - Frame captures
- `/api/users/` - User management
- `/api/sessions/aggregate_report/` - Aggregate analytics

### Django Admin
- `/django-admin/` - Full Django admin panel

## Next Steps

1. Upload some test videos as admin
2. Create additional user accounts if needed
3. Test the emotion detection with different videos
4. Review the aggregate reports
5. Customize the system as needed

## Support

For issues or questions:
1. Check the main README.md
2. Review the code comments
3. Check Django/DeepFace documentation
