# Video Emotion Analysis System

An interactive web application with role-based access (Admin & User) that plays videos, captures user facial expressions via webcam (3 photos per second), analyzes emotions using AI, and generates comprehensive reports.

## Features

### Admin Features
- 👨‍💼 **Admin Dashboard**: Overview of all system statistics
- 🎬 **Video Management**: Upload, manage, and delete videos
- 👥 **User Management**: View and manage user accounts
- 📊 **Aggregate Reports**: View overall analytics across all sessions
- 📈 **Video Analytics**: See engagement metrics for each video

### User Features
- 🎬 **Video Library**: Browse and select videos to watch
- 📷 **Real-time Webcam Capture**: Automatically captures 3 frames per second during video playback
- 🤖 **AI Emotion Detection**: Analyzes facial expressions using DeepFace
- 📊 **Personal Reports**: View your session analytics with charts
- 🎯 **Engagement Scoring**: See your emotional engagement with the content

## Detected Emotions

- Happy 😊
- Sad 😢
- Angry 😠
- Surprise 😲
- Fear 😨
- Disgust 🤢
- Neutral 😐

## Project Structure

```
quickstart/
├── models.py           # Database models (VideoSession, CapturedFrame)
├── views.py            # API endpoints and page views
├── serializers.py      # REST API serializers
├── services.py         # Business logic (EmotionDetectionService, SessionAnalyticsService)
├── admin.py            # Django admin configuration
├── templates/
│   └── quickstart/
│       ├── video_session.html  # Main session page
│       └── report.html         # Analytics report page
└── static/
    └── quickstart/
        └── js/
            └── video-session.js  # Frontend session manager
```

## Setup Instructions

### 1. Install Dependencies

```bash
pip install django djangorestframework pillow deepface opencv-python tensorflow tf-keras
```

### 2. Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 3. Create Demo Users

```bash
python manage.py shell < create_demo_users.py
```

This creates two demo accounts:
- **Admin**: username=`admin`, password=`admin123`
- **User**: username=`user`, password=`user123`

### 4. Run the Server

```bash
python manage.py runserver
```

### 5. Access the Application

- **Login Page**: http://127.0.0.1:8000/
- **Django Admin**: http://127.0.0.1:8000/django-admin/

## Demo Credentials

### Admin Account
- Username: `admin`
- Password: `admin123`
- Access: Full system access, video management, user management, aggregate reports

### User Account
- Username: `user`
- Password: `user123`
- Access: Video library, session recording, personal reports

## How to Use

### For Admin Users

1. **Login**: Go to http://127.0.0.1:8000/ and login with admin credentials
2. **Dashboard**: View system overview with total videos, users, sessions, and captures
3. **Manage Videos**:
   - Click "Manage Videos"
   - Upload new videos with title and description
   - View video statistics (sessions, engagement)
   - Delete videos
4. **Manage Users**: View all registered users and their activity
5. **View Reports**: See aggregate analytics across all sessions
   - Overall emotion distribution
   - Most popular videos
   - Active users

### For Regular Users

1. **Login**: Go to http://127.0.0.1:8000/ and login with user credentials
2. **Select Video**: Browse the video library and click on a video
3. **Start Session**:
   - Allow webcam access when prompted
   - Click "Start Session" to begin
   - Watch the video while your expressions are captured (3 per second)
   - Click "Stop Session" when done
4. **View Report**: See your personal analytics including:
   - Total captures and detection rate
   - Dominant emotion
   - Engagement score
   - Emotion distribution chart

### Django Admin Panel

Access http://127.0.0.1:8000/django-admin/ for full database management:
- View all sessions and captured frames
- See emotion summaries
- Browse image previews
- Filter by emotions and dates

## API Endpoints

### Sessions
- `POST /api/sessions/` - Create new session
- `GET /api/sessions/` - List all sessions
- `GET /api/sessions/{id}/` - Get session details
- `POST /api/sessions/{id}/complete/` - Mark session complete
- `GET /api/sessions/{id}/report/` - Get analytics report

### Captures
- `POST /api/captures/` - Upload captured frame
- `GET /api/captures/` - List all captures
- `GET /api/captures/{id}/` - Get capture details

## Modular Architecture

### Services Layer (`services.py`)

**EmotionDetectionService**
- Handles all emotion detection logic
- Tries multiple detection backends for reliability
- Returns structured results with error handling

**SessionAnalyticsService**
- Generates comprehensive session reports
- Calculates emotion statistics and percentages
- Computes engagement scores

### Frontend Module (`video-session.js`)

**VideoSessionManager Class**
- Manages video playback
- Controls webcam capture
- Handles API communication
- Updates real-time statistics
- Provides clean separation of concerns

## Technical Details

### Capture Rate
- 3 frames per second (every 333ms)
- Automatic during video playback
- Stops when video ends or user stops session

### Emotion Detection
- Uses DeepFace library with multiple backends
- Falls back to alternative backends if primary fails
- Provides confidence scores for each emotion
- Handles cases where no face is detected

### Data Storage
- All captures stored in database with timestamps
- Images saved to `media/captures/`
- JSON fields store detailed emotion data
- Efficient querying for analytics

## Browser Requirements

- Modern browser with webcam support
- JavaScript enabled
- Webcam permissions granted

## Performance Tips

- Use videos under 1 minute for best performance
- Ensure good lighting for better face detection
- Face the camera directly
- Close other applications using the webcam

## Troubleshooting

**Webcam not working:**
- Check browser permissions
- Ensure no other app is using the webcam
- Try refreshing the page

**Emotion detection failing:**
- Ensure good lighting
- Face the camera directly
- Check that face is clearly visible
- Wait for models to download on first run

**Slow performance:**
- Close unnecessary browser tabs
- Use shorter videos
- Check CPU usage

## Future Enhancements

- Multiple user support
- Video library management
- Export reports to PDF
- Real-time emotion overlay on video
- Comparison between multiple sessions
- Custom emotion training

## License

MIT License
