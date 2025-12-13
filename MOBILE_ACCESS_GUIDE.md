# Mobile Access Guide for Django Video Emotion Analysis

## Method 1: Local Network Access (Recommended for Testing)

### Step 1: Find Your Computer's IP Address

**On Windows:**
```bash
ipconfig
```
Look for "IPv4 Address" under your active network adapter (usually starts with 192.168.x.x or 10.0.x.x)

**On Mac/Linux:**
```bash
ifconfig
```
or
```bash
ip addr show
```

### Step 2: Start Django Server on All Interfaces

Instead of running:
```bash
python manage.py runserver
```

Run:
```bash
python manage.py runserver 0.0.0.0:8000
```

This makes the server accessible from any device on your network.

### Step 3: Access from Mobile

On your mobile device (connected to the same WiFi):
1. Open a web browser
2. Go to: `http://YOUR_IP_ADDRESS:8000`
   - Example: `http://192.168.1.100:8000`

### Step 4: Login
Use the same credentials:
- Admin: `admin` / `admin123`
- User: `user` / `user123`

---

## Method 2: Using ngrok (For Remote Access)

If you want to access your site from anywhere (not just local network):

### Step 1: Install ngrok
Download from: https://ngrok.com/download

### Step 2: Start Your Django Server
```bash
python manage.py runserver 8000
```

### Step 3: Start ngrok
In a new terminal:
```bash
ngrok http 8000
```

### Step 4: Use the ngrok URL
ngrok will provide a public URL like:
```
https://abc123.ngrok.io
```

Access this URL from any device, anywhere in the world!

**Note:** Add the ngrok URL to ALLOWED_HOSTS in settings.py:
```python
ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'abc123.ngrok.io']
```

---

## Method 3: Deploy to Cloud (For Production)

For permanent mobile access, deploy to:

### Option A: Heroku (Free Tier Available)
1. Create Heroku account
2. Install Heroku CLI
3. Deploy with Git

### Option B: PythonAnywhere (Free Tier Available)
1. Create account at pythonanywhere.com
2. Upload your code
3. Configure WSGI

### Option C: AWS/Azure/Google Cloud
More complex but fully customizable

---

## Troubleshooting

### Can't Connect from Mobile?

1. **Check Firewall:**
   - Windows: Allow Python through Windows Firewall
   - Mac: System Preferences → Security & Privacy → Firewall

2. **Verify Same Network:**
   - Both devices must be on the same WiFi network
   - Corporate/School networks may block device-to-device communication

3. **Check IP Address:**
   - Make sure you're using the correct IP address
   - IP addresses can change, especially on DHCP networks

4. **Port Issues:**
   - Try a different port: `python manage.py runserver 0.0.0.0:8080`
   - Access via: `http://YOUR_IP:8080`

### Camera Not Working on Mobile?

The webcam emotion detection requires:
- HTTPS connection (use ngrok for this)
- Camera permissions granted in browser
- Modern browser (Chrome, Safari, Firefox)

---

## Security Notes

⚠️ **Important for Production:**

1. **Never use `ALLOWED_HOSTS = ['*']` in production**
   - Specify exact domains: `ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com']`

2. **Change SECRET_KEY**
   - Generate a new secret key for production
   - Keep it secret and secure

3. **Set DEBUG = False**
   - Never run with DEBUG=True in production

4. **Use HTTPS**
   - Required for camera access
   - Use Let's Encrypt for free SSL certificates

5. **Configure CSRF Settings**
   - Set CSRF_TRUSTED_ORIGINS for your domain

---

## Quick Start Commands

### For Local Network Testing:
```bash
# Activate virtual environment
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux

# Start server on all interfaces
python manage.py runserver 0.0.0.0:8000

# Find your IP
ipconfig  # Windows
ifconfig  # Mac/Linux

# Access from mobile
# http://YOUR_IP:8000
```

### For ngrok (Remote Access):
```bash
# Terminal 1: Start Django
python manage.py runserver 8000

# Terminal 2: Start ngrok
ngrok http 8000

# Use the https URL provided by ngrok
```

---

## Mobile-Optimized Features

The website is already responsive and includes:
- ✅ Responsive design for all screen sizes
- ✅ Touch-friendly buttons and controls
- ✅ Mobile-optimized navigation
- ✅ Adaptive layouts for tablets and phones
- ✅ Mobile camera support for emotion detection

---

## Need Help?

Common issues and solutions:
- **"This site can't be reached"** → Check firewall and IP address
- **"Invalid HTTP_HOST header"** → Add your IP/domain to ALLOWED_HOSTS
- **Camera not working** → Use HTTPS (ngrok) and grant permissions
- **Slow performance** → Reduce video quality or frame rate

For more help, check Django documentation: https://docs.djangoproject.com/
