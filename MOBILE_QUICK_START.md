# 📱 Quick Start: Access on Mobile

## Windows Users

1. **Double-click** `start_mobile_server.bat`
2. The script will show your IP address
3. Open your mobile browser and go to the displayed URL

Example: `http://192.168.1.100:8000`

---

## Mac/Linux Users

1. **Make script executable** (first time only):
   ```bash
   chmod +x start_mobile_server.sh
   ```

2. **Run the script**:
   ```bash
   ./start_mobile_server.sh
   ```

3. Open your mobile browser and go to the displayed URL

---

## Manual Method

If the scripts don't work:

1. **Find your IP address:**
   - Windows: Open CMD and type `ipconfig`
   - Mac/Linux: Open Terminal and type `ifconfig`
   - Look for IPv4 address (usually 192.168.x.x)

2. **Start server:**
   ```bash
   python manage.py runserver 0.0.0.0:8000
   ```

3. **Access from mobile:**
   - Open browser on your phone
   - Go to: `http://YOUR_IP_ADDRESS:8000`
   - Example: `http://192.168.1.100:8000`

---

## ⚠️ Important Notes

- **Same WiFi Network**: Your phone and computer must be on the same WiFi
- **Firewall**: You may need to allow Python through your firewall
- **Camera Access**: For emotion detection, you'll need HTTPS (use ngrok)

---

## 🔒 For Remote Access (Outside Your Network)

Use **ngrok** for secure remote access:

1. Download ngrok: https://ngrok.com/download
2. Start Django: `python manage.py runserver 8000`
3. In new terminal: `ngrok http 8000`
4. Use the HTTPS URL provided by ngrok

---

## 📞 Need Help?

See the full guide: `MOBILE_ACCESS_GUIDE.md`
