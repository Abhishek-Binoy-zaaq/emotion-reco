# System Architecture

## Overview

The Video Emotion Analysis System is built with a modular, role-based architecture separating concerns between Admin and User functionalities.

## Architecture Layers

### 1. Data Layer (models.py)
- **Video**: Stores uploaded videos with metadata
- **VideoSession**: Tracks user viewing sessions
- **CapturedFrame**: Stores individual webcam captures with emotion data
- **UploadedImage**: Legacy single image uploads

### 2. Service Layer (services.py)
- **EmotionDetectionService**: Handles AI emotion detection
  - Multiple backend support (opencv, ssd, retinaface)
  - Error handling and fallback mechanisms
  - Numpy to JSON conversion
  
- **SessionAnalyticsService**: Generates analytics reports
  - Emotion distribution calculations
  - Engagement scoring
  - Timeline generation

### 3. API Layer (views.py + serializers.py)
- **VideoViewSet**: Video CRUD operations (Admin only)
- **VideoSessionViewSet**: Session management
- **CapturedFrameViewSet**: Frame upload and analysis
- **UserViewSet**: User management (Admin only)

### 4. Presentation Layer (templates/)

#### Admin Interface
- **admin_dashboard.html**: System overview
- **admin_videos.html**: Video management
- **admin_users.html**: User management
- **admin_reports.html**: Aggregate analytics

#### User Interface
- **user_dashboard.html**: Video library
- **user_session.html**: Video playback + webcam capture
- **user_report.html**: Personal session analytics

#### Authentication
- **login.html**: Unified login page

## Data Flow

### User Session Flow
```
1. User selects video → user_dashboard.html
2. Session created → POST /api/sessions/
3. Video plays + webcam captures → user_session.html
4. Frames uploaded → POST /api/captures/
5. AI analyzes each frame → EmotionDetectionService
6. Session completed → POST /api/sessions/{id}/complete/
7. Report generated → GET /api/sessions/{id}/report/
8. User views report → user_report.html
```

### Admin Video Upload Flow
```
1. Admin uploads video → admin_videos.html
2. Video saved → POST /api/videos/
3. Video available to all users
4. Admin views stats → GET /api/videos/stats/
```

### Emotion Detection Flow
```
1. Frame captured from webcam
2. Uploaded to server → POST /api/captures/
3. EmotionDetectionService.analyze_image()
4. Try multiple backends (opencv → ssd → retinaface)
5. Extract emotions and confidence scores
6. Convert numpy types to JSON
7. Save to database
8. Return results to frontend
```

## Security Model

### Role-Based Access Control

#### Admin Users (is_staff=True)
- Full system access
- Video upload/delete
- User management
- Aggregate reports
- All API endpoints

#### Regular Users (is_staff=False)
- Video library access
- Own session management
- Personal reports only
- Limited API access

### Authentication
- Django session-based authentication
- CSRF protection on all POST requests
- Login required for all pages except login
- Role checks using @user_passes_test decorator

## Database Schema

```
Video
├── id (PK)
├── title
├── description
├── video_file
├── duration
├── uploaded_by (FK → User)
├── uploaded_at
└── is_active

VideoSession
├── id (PK)
├── video (FK → Video)
├── user (FK → User)
├── started_at
├── completed_at
└── is_completed

CapturedFrame
├── id (PK)
├── session (FK → VideoSession)
├── image
├── timestamp
├── expression
├── expression_confidence
└── all_expressions (JSON)
```

## Frontend Architecture

### JavaScript Modules

#### video-session.js (User Session)
- VideoSessionManager class
- Webcam initialization
- Frame capture (3 per second)
- Real-time statistics
- Session lifecycle management

#### admin-videos.js (Admin Video Management)
- Video listing
- Upload modal
- Delete functionality
- Statistics display

### CSS Organization
- **admin-common.css**: Shared styles for all admin pages
- Inline styles for specific pages
- Responsive grid layouts
- Consistent color scheme (#667eea primary)

## API Endpoints

### Public Endpoints
- `POST /api-auth/login/` - Login
- `POST /api-auth/logout/` - Logout

### Authenticated Endpoints
- `GET /api/videos/` - List videos
- `GET /api/videos/{id}/` - Video details
- `POST /api/sessions/` - Create session
- `POST /api/captures/` - Upload frame
- `GET /api/sessions/{id}/report/` - Session report

### Admin-Only Endpoints
- `POST /api/videos/` - Upload video
- `DELETE /api/videos/{id}/` - Delete video
- `GET /api/users/` - List users
- `GET /api/sessions/aggregate_report/` - Aggregate analytics

## Scalability Considerations

### Current Implementation
- Synchronous emotion detection
- Local file storage
- SQLite database
- Single-threaded processing

### Production Recommendations
1. **Async Processing**: Use Celery for emotion detection
2. **Cloud Storage**: S3/Azure for videos and captures
3. **Database**: PostgreSQL for better performance
4. **Caching**: Redis for session data
5. **Load Balancing**: Multiple app servers
6. **CDN**: For video delivery

## Modularity Benefits

### Easy to Extend
- Add new emotion detection backends
- Implement new analytics metrics
- Create additional user roles
- Add real-time notifications

### Easy to Test
- Service layer isolated from views
- Mock emotion detection for testing
- Separate frontend/backend logic

### Easy to Maintain
- Clear separation of concerns
- Consistent naming conventions
- Comprehensive comments
- Modular file structure

## Technology Stack

- **Backend**: Django 5.2, Django REST Framework
- **AI/ML**: DeepFace, TensorFlow, OpenCV
- **Frontend**: Vanilla JavaScript, Chart.js
- **Database**: SQLite (dev), PostgreSQL (prod recommended)
- **Authentication**: Django Auth System
- **File Storage**: Local filesystem (dev), S3 (prod recommended)
