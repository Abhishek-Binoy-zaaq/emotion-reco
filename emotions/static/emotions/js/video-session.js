/**
 * Video Session Manager
 * Handles video playback, webcam capture, and emotion analysis
 */

class VideoSessionManager {
    constructor() {
        this.sessionId = null;
        this.isRecording = false;
        this.captureInterval = null;
        this.webcamStream = null;
        this.captureCount = 0;
        this.successfulDetections = 0;
        this.emotionCounts = {};
        
        // DOM elements
        this.videoFile = document.getElementById('videoFile');
        this.videoPlayer = document.getElementById('videoPlayer');
        this.webcam = document.getElementById('webcam');
        this.canvas = document.getElementById('canvas');
        this.startBtn = document.getElementById('startBtn');
        this.stopBtn = document.getElementById('stopBtn');
        this.viewReportBtn = document.getElementById('viewReportBtn');
        this.status = document.getElementById('status');
        this.videoInfo = document.getElementById('videoInfo');
        this.videoName = document.getElementById('videoName');
        this.videoDuration = document.getElementById('videoDuration');
        this.currentEmotion = document.getElementById('currentEmotion');
        
        // Stats elements
        this.captureCountEl = document.getElementById('captureCount');
        this.detectionRateEl = document.getElementById('detectionRate');
        this.currentTimeEl = document.getElementById('currentTime');
        this.dominantEmotionEl = document.getElementById('dominantEmotion');
        
        this.init();
    }
    
    init() {
        this.videoFile.addEventListener('change', (e) => this.handleVideoSelect(e));
        this.startBtn.addEventListener('click', () => this.startSession());
        this.stopBtn.addEventListener('click', () => this.stopSession());
        this.viewReportBtn.addEventListener('click', () => this.viewReport());
        this.videoPlayer.addEventListener('timeupdate', () => this.updateVideoTime());
        this.videoPlayer.addEventListener('ended', () => this.handleVideoEnd());
        
        this.initWebcam();
    }
    
    async initWebcam() {
        try {
            this.webcamStream = await navigator.mediaDevices.getUserMedia({ 
                video: { width: 640, height: 480 } 
            });
            this.webcam.srcObject = this.webcamStream;
            this.updateStatus('Webcam ready', 'success');
        } catch (error) {
            this.updateStatus('Error accessing webcam: ' + error.message, 'warning');
            console.error('Webcam error:', error);
        }
    }
    
    handleVideoSelect(event) {
        const file = event.target.files[0];
        if (!file) return;
        
        const url = URL.createObjectURL(file);
        this.videoPlayer.src = url;
        
        this.videoPlayer.onloadedmetadata = () => {
            const duration = Math.floor(this.videoPlayer.duration);
            this.videoName.textContent = file.name;
            this.videoDuration.textContent = this.formatTime(duration);
            this.videoInfo.classList.remove('hidden');
            this.startBtn.disabled = false;
            this.updateStatus('Video loaded. Click "Start Session" to begin.', 'info');
        };
    }
    
    async startSession() {
        try {
            this.updateStatus('Creating session...', 'info');
            
            // Create session
            const sessionData = {
                video_name: this.videoName.textContent,
                video_duration: Math.floor(this.videoPlayer.duration)
            };
            
            const response = await fetch('/api/sessions/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCookie('csrftoken')
                },
                body: JSON.stringify(sessionData)
            });
            
            if (!response.ok) throw new Error('Failed to create session');
            
            const session = await response.json();
            this.sessionId = session.id;
            
            // Start recording
            this.isRecording = true;
            this.captureCount = 0;
            this.successfulDetections = 0;
            this.emotionCounts = {};
            
            this.startBtn.disabled = true;
            this.stopBtn.disabled = false;
            this.videoFile.disabled = true;
            
            // Start video playback
            this.videoPlayer.play();
            
            // Start capturing frames (3 per second = every 333ms)
            this.captureInterval = setInterval(() => this.captureFrame(), 333);
            
            this.updateStatus('Session started! Recording emotions...', 'success');
            
        } catch (error) {
            this.updateStatus('Error starting session: ' + error.message, 'warning');
            console.error('Start session error:', error);
        }
    }
    
    async stopSession() {
        this.isRecording = false;
        clearInterval(this.captureInterval);
        this.videoPlayer.pause();
        
        this.stopBtn.disabled = true;
        this.updateStatus('Completing session...', 'info');
        
        try {
            // Mark session as complete
            await fetch(`/api/sessions/${this.sessionId}/complete/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': this.getCookie('csrftoken')
                }
            });
            
            this.updateStatus('Session completed! Click "View Report" to see results.', 'success');
            this.viewReportBtn.disabled = false;
            
        } catch (error) {
            this.updateStatus('Error completing session: ' + error.message, 'warning');
            console.error('Stop session error:', error);
        }
    }
    
    async captureFrame() {
        if (!this.isRecording) return;
        
        const context = this.canvas.getContext('2d');
        this.canvas.width = this.webcam.videoWidth;
        this.canvas.height = this.webcam.videoHeight;
        
        // Draw webcam frame to canvas
        context.drawImage(this.webcam, 0, 0);
        
        // Convert to blob
        this.canvas.toBlob(async (blob) => {
            if (!blob) return;
            
            const formData = new FormData();
            formData.append('image', blob, `capture_${Date.now()}.jpg`);
            formData.append('session', this.sessionId);
            formData.append('timestamp', this.videoPlayer.currentTime.toFixed(2));
            
            try {
                const response = await fetch('/api/captures/', {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': this.getCookie('csrftoken')
                    },
                    body: formData
                });
                
                if (response.ok) {
                    const data = await response.json();
                    this.captureCount++;
                    this.updateCaptureStats(data);
                }
                
            } catch (error) {
                console.error('Capture error:', error);
            }
        }, 'image/jpeg', 0.8);
    }
    
    updateCaptureStats(captureData) {
        // Update capture count
        this.captureCountEl.textContent = this.captureCount;
        
        // Update emotion counts
        if (captureData.expression && captureData.expression !== 'error' && captureData.expression !== 'no_face_detected') {
            this.successfulDetections++;
            this.emotionCounts[captureData.expression] = (this.emotionCounts[captureData.expression] || 0) + 1;
            
            // Update current emotion display
            const emoji = this.getEmotionEmoji(captureData.expression);
            this.currentEmotion.innerHTML = `
                <div class="emotion-indicator">
                    ${emoji} ${captureData.expression} (${captureData.expression_confidence.toFixed(1)}%)
                </div>
            `;
        }
        
        // Update detection rate
        const rate = (this.successfulDetections / this.captureCount * 100).toFixed(1);
        this.detectionRateEl.textContent = rate + '%';
        
        // Update dominant emotion
        if (Object.keys(this.emotionCounts).length > 0) {
            const dominant = Object.entries(this.emotionCounts)
                .sort((a, b) => b[1] - a[1])[0][0];
            this.dominantEmotionEl.textContent = dominant;
        }
    }
    
    updateVideoTime() {
        const current = Math.floor(this.videoPlayer.currentTime);
        this.currentTimeEl.textContent = this.formatTime(current);
    }
    
    handleVideoEnd() {
        if (this.isRecording) {
            this.stopSession();
        }
    }
    
    viewReport() {
        window.location.href = `/report/${this.sessionId}/`;
    }
    
    updateStatus(message, type = 'info') {
        this.status.textContent = message;
        this.status.className = `status ${type}`;
    }
    
    formatTime(seconds) {
        const mins = Math.floor(seconds / 60);
        const secs = seconds % 60;
        return `${mins}:${secs.toString().padStart(2, '0')}`;
    }
    
    getEmotionEmoji(emotion) {
        const emojis = {
            'happy': '😊',
            'sad': '😢',
            'angry': '😠',
            'surprise': '😲',
            'fear': '😨',
            'disgust': '🤢',
            'neutral': '😐'
        };
        return emojis[emotion] || '😶';
    }
    
    getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    new VideoSessionManager();
});
