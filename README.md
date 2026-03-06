📹 Zoom Attendance Tracker Bot
A containerized Python bot that automatically tracks camera on/off time during Zoom meetings and marks attendance based on a configurable threshold. Perfect for educators, trainers, and team leads who need to verify participation via video engagement.

✨ Features
✅ Automatically joins Zoom meetings as a silent participant

✅ Tracks camera on/off events in real-time for all participants

✅ Calculates total camera-on time per person

✅ Marks attendance based on a configurable threshold (default: 45 minutes)

✅ Generates CSV reports with detailed attendance data

✅ Runs in Docker – no installation hassles, works on Windows/Mac/Linux

✅ Privacy-focused – all data stays local, no external servers

📋 Prerequisites
Before you begin, ensure you have:

Docker Desktop (with WSL2 integration on Windows)

Zoom Account (free or paid)

Zoom App credentials (from Zoom Marketplace)

Basic familiarity with command line

🚀 Quick Start
1️⃣ Clone the Repository
bash
git clone https://github.com/PUSHPAKSARODE07/zoom-video-attendance-bot-.git
cd zoom-video-attendance-bot-
2️⃣ Download Zoom Meeting SDK
Go to Zoom Marketplace → Develop → Build App

Create a General App

Enable Meeting SDK in Features tab

Download Linux-x86_64 SDK

Extract to zoomsdk/ folder in project root

3️⃣ Configure Your Credentials
Edit bot.py and update these values:

python
ZOOM_CLIENT_ID = "your_client_id_here"
ZOOM_CLIENT_SECRET = "your_client_secret_here"
ZOOM_ACCOUNT_ID = "your_account_id_here"
MEETING_ID = "94245179556"  # Your meeting ID
MEETING_PASSWORD = ""        # Meeting password (if any)
ATTENDANCE_THRESH_MINUTES = 45  # Minutes to be marked present
4️⃣ Build and Run
bash
docker-compose build
docker-compose up
5️⃣ Stop and Get Report
Press Ctrl+C to stop the bot – it will automatically generate attendance_report.csv

📊 Sample Output
Console:

text
==================================================
ATTENDANCE REPORT
==================================================
pushpak: 47.5 minutes - ✅ PRESENT
John Doe: 12.3 minutes - ❌ ABSENT
Jane Smith: 45.0 minutes - ✅ PRESENT
==================================================
📁 Detailed report saved to 'attendance_report.csv'
CSV File:

csv
name,camera_on_minutes,present
pushpak,47.5,True
John Doe,12.3,False
Jane Smith,45.0,True
🛠️ Configuration Options
Variable	Description	Default
ZOOM_CLIENT_ID	Your Zoom app Client ID	Required
ZOOM_CLIENT_SECRET	Your Zoom app Client Secret	Required
ZOOM_ACCOUNT_ID	Your Zoom Account ID	Required
MEETING_ID	Meeting to join	Required
MEETING_PASSWORD	Meeting password (if any)	""
ATTENDANCE_THRESHOLD_MINUTES	Minimum camera-on time for attendance	45
🐳 Docker Setup
The bot runs in a Docker container with all dependencies pre-installed:

Dockerfile includes:

Python 3.10 slim image

All system libraries for Zoom SDK (X11, OpenGL, audio, etc.)

Non-root user for security

Pre-installed Python packages

docker-compose.yml:

yaml
services:
  bot:
    image: zoom-attendance-bot
    build: .
    container_name: zoom-attendance-bot
    volumes:
      - ./bot.py:/app/bot.py
      - ./attendance_report.csv:/app/attendance_report.csv
    command: python bot.py
📁 Project Structure
text
zoom-attendance-bot/
├── bot.py                 # Main bot code
├── Dockerfile             # Docker configuration
├── docker-compose.yml     # Docker Compose setup
├── requirements.txt       # Python dependencies
├── .gitignore             # Git ignore rules
├── README.md              # This file
└── zoomsdk/               # Zoom SDK (download separately)
    ├── lib/
    ├── include/
    └── ...
🔧 Troubleshooting
❌ "Failed to get OAuth token"
Verify your Client ID, Secret, and Account ID are correct

Ensure your Zoom app is activated in the Marketplace

❌ "Bot cannot join meeting"
Check that the meeting is actively running

Verify the Meeting ID and password

Ensure your Zoom app has Meeting SDK enabled

❌ "ImportError: cannot import name..."
The Python bindings may have changed. Run with diagnostics:

bash
python -c "import zoom_meeting_sdk; print(dir(zoom_meeting_sdk))"
❌ Docker build fails
Ensure Docker Desktop is running

Try: docker-compose build --no-cache

Check disk space: df -h

❌ Git push stuck with LFS
If you're having issues pushing to GitHub due to large SDK files:

bash
GIT_LFS_SKIP_PUSH=1 git push origin main
Or follow the cleanup steps in our GitHub Guide

🔒 Privacy & Data
All data stays on your machine – no cloud uploads

No external APIs beyond Zoom's SDK

Attendance reports are saved locally as CSV files

No video/audio recording – only camera on/off events
