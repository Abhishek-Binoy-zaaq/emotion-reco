@echo off
echo ========================================
echo Django Video Emotion Analysis
echo Mobile Access Server
echo ========================================
echo.

REM Activate virtual environment
call venv\Scripts\activate

echo Finding your IP address...
echo.
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /c:"IPv4 Address"') do (
    set IP=%%a
    set IP=!IP:~1!
    echo Your IP Address: !IP!
    echo.
    echo Access from mobile browser:
    echo http://!IP!:8000
    echo.
)

echo ========================================
echo Starting Django server on all interfaces...
echo Press Ctrl+C to stop the server
echo ========================================
echo.

python manage.py runserver 0.0.0.0:8000

pause
