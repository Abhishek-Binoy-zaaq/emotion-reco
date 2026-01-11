#!/bin/bash

echo "========================================"
echo "Django Video Emotion Analysis"
echo "Mobile Access Server"
echo "========================================"
echo ""

# Activate virtual environment
source venv/bin/activate

echo "Finding your IP address..."
echo ""

# Get IP address (works on most Unix systems)
if command -v ip &> /dev/null; then
    IP=$(ip addr show | grep "inet " | grep -v 127.0.0.1 | awk '{print $2}' | cut -d/ -f1 | head -n1)
elif command -v ifconfig &> /dev/null; then
    IP=$(ifconfig | grep "inet " | grep -v 127.0.0.1 | awk '{print $2}' | head -n1)
fi

if [ -n "$IP" ]; then
    echo "Your IP Address: $IP"
    echo ""
    echo "Access from mobile browser:"
    echo "http://$IP:8000"
    echo ""
else
    echo "Could not detect IP address automatically."
    echo "Run 'ifconfig' or 'ip addr' to find your IP address manually."
    echo ""
fi

echo "========================================"
echo "Starting Django server on all interfaces..."
echo "Press Ctrl+C to stop the server"
echo "========================================"
echo ""

python manage.py runserver 0.0.0.0:8000
