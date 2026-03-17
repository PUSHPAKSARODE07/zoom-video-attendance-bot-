import os
import time
import csv
import requests
from datetime import datetime
import zoom_meeting_sdk as zmp

# ===== CONFIGURATION – YOUR CREDENTIALS =====
ZOOM_CLIENT_ID = "YOUR_CLIENT_ID"
ZOOM_CLIENT_SECRET = "YOUR_CLIENT_SECRET"
ZOOM_ACCOUNT_ID = "YOUR_ACCOUNT_ID"
MEETING_ID = "94245179556"          # Replace with your meeting ID
MEETING_PASSWORD = ""                # Meeting password if any
ATTENDANCE_THRESHOLD_MINUTES = 45
# ============================================

# Global storage for participant data
participant_data = {}

class MyAuthCallbacks(zmp.AuthServiceEventCallbacks):
    def onAuthenticationReturn(self, result):
        print(f"Authentication result: {result}")
        if result == zmp.AUTHRET_SUCCESS:
            print("✅ Authentication successful.")
        else:
            print("❌ Authentication failed. Check your credentials.")

class MyMeetingCallbacks(zmp.MeetingServiceEventCallbacks):
    def onMeetingStatusChanged(self, status, result):
        status_names = {
            zmp.MEETING_STATUS_IDLE: "IDLE",
            zmp.MEETING_STATUS_CONNECTING: "CONNECTING",
            zmp.MEETING_STATUS_WAITINGFORHOST: "WAITING_FOR_HOST",
            zmp.MEETING_STATUS_INMEETING: "IN_MEETING",
            zmp.MEETING_STATUS_DISCONNECTING: "DISCONNECTING",
            zmp.MEETING_STATUS_RECONNECTING: "RECONNECTING",
            zmp.MEETING_STATUS_FAILED: "FAILED",
            zmp.MEETING_STATUS_ENDED: "ENDED",
            zmp.MEETING_STATUS_LOCKED: "LOCKED",
            zmp.MEETING_STATUS_UNLOCKED: "UNLOCKED",
        }
        print(f"Meeting status: {status_names.get(status, status)}")
        if status == zmp.MEETING_STATUS_INMEETING:
            print("🎉 Bot has joined the meeting!")

    def onUserJoin(self, user_list):
        for user_id in user_list:
            user_obj = self.getUserByID(user_id)
            if user_obj:
                user_name = user_obj.getUserName()
                print(f"--> User joined: {user_name} (ID: {user_id})")
                if user_id not in participant_data:
                    participant_data[user_id] = {'name': user_name, 'camera_on_events': []}
            else:
                print(f"--> Unknown user joined (ID: {user_id})")

    def onUserLeft(self, user_list):
        for user_id in user_list:
            user_name = participant_data.get(user_id, {}).get('name', 'Unknown')
            print(f"<-- User left: {user_name} (ID: {user_id})")

    def onUserVideoStatusChanged(self, user_id, status):
        user_name = participant_data.get(user_id, {}).get('name', 'Unknown')
        status_str = "ON" if status == zmp.Video_ON else "OFF"
        timestamp = datetime.now()
        print(f"[{timestamp.strftime('%H:%M:%S')}] Video {status_str}: {user_name} (ID: {user_id})")

        if user_id in participant_data:
            participant_data[user_id]['camera_on_events'].append({
                'timestamp': timestamp,
                'status': status
            })
        else:
            participant_data[user_id] = {'name': user_name, 'camera_on_events': [{'timestamp': timestamp, 'status': status}]}

def get_oauth_token():
    token_url = "https://zoom.us/oauth/token"
    data = {
        "grant_type": "account_credentials",
        "account_id": ZOOM_ACCOUNT_ID
    }
    response = requests.post(token_url, auth=(ZOOM_CLIENT_ID, ZOOM_CLIENT_SECRET), data=data)
    if response.status_code != 200:
        print(f"Failed to get OAuth token: {response.status_code} - {response.text}")
        return None
    return response.json()["access_token"]

def analyze_and_mark_attendance():
    print("\n" + "="*50)
    print("ATTENDANCE REPORT")
    print("="*50)

    attendance_results = []

    for user_id, info in participant_data.items():
        user_name = info['name']
        events = info['camera_on_events']

        if not events:
            print(f"{user_name}: No video events recorded.")
            attendance_results.append({'name': user_name, 'camera_on_minutes': 0, 'present': False})
            continue

        sorted_events = sorted(events, key=lambda x: x['timestamp'])
        total_on_seconds = 0
        camera_on_start = None

        for event in sorted_events:
            if event['status'] == zmp.Video_ON:
                camera_on_start = event['timestamp']
            elif event['status'] == zmp.Video_OFF and camera_on_start:
                duration = (event['timestamp'] - camera_on_start).total_seconds()
                total_on_seconds += max(0, duration)
                camera_on_start = None

        if camera_on_start:
            last_time = sorted_events[-1]['timestamp']
            duration = (last_time - camera_on_start).total_seconds()
            total_on_seconds += max(0, duration)

        total_on_minutes = total_on_seconds / 60
        present = total_on_minutes >= ATTENDANCE_THRESHOLD_MINUTES

        attendance_results.append({
            'name': user_name,
            'camera_on_minutes': round(total_on_minutes, 2),
            'present': present
        })

    for r in attendance_results:
        status = "✅ PRESENT" if r['present'] else "❌ ABSENT"
        print(f"{r['name']}: {r['camera_on_minutes']} minutes - {status}")

    with open('attendance_report.csv', 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['name', 'camera_on_minutes', 'present'])
        writer.writeheader()
        writer.writerows(attendance_results)
    print("\n📁 Detailed report saved to 'attendance_report.csv'")

def main():
    print("Obtaining OAuth token...")
    token = get_oauth_token()
    if not token:
        return
    print("✅ OAuth token obtained.")

    print("Initializing Zoom Meeting SDK...")
    init_param = zmp.InitParam()
    init_param.strWebDomain = "zoom.us"
    init_param.enableLogByDefault = True
    init_param.emLanguageID = 0

    ret = zmp.InitSDK(init_param)
    if ret != zmp.SDKERR_SUCCESS:
        print(f"Failed to initialize SDK, error code: {ret}")
        return
    print("SDK initialized successfully.")

    auth_service = zmp.CreateAuthService()
    if not auth_service:
        print("Failed to create auth service")
        zmp.CleanUPSDK()
        return

    auth_callbacks = MyAuthCallbacks()
    auth_service.SetEvent(auth_callbacks)

    meeting_service = zmp.CreateMeetingService()
    if not meeting_service:
        print("Failed to create meeting service")
        zmp.DestroyAuthService(auth_service)
        zmp.CleanUPSDK()
        return

    meeting_callbacks = MyMeetingCallbacks()
    meeting_service.SetEvent(meeting_callbacks)

    ctx = zmp.AuthContext()
    ctx.jwt_token = token

    auth_result = auth_service.SDKAuth(ctx)
    if auth_result != zmp.SDKERR_SUCCESS:
        print(f"SDKAuth failed with error: {auth_result}")
        zmp.CleanUPSDK()
        return

    print("Waiting for authentication to complete...")
    time.sleep(5)

    print(f"Attempting to join meeting {MEETING_ID}...")
    join_param = zmp.JoinParam()
    join_param.meetingNumber = int(MEETING_ID)
    join_param.userName = "AttendanceBot"
    join_param.psw = MEETING_PASSWORD
    join_param.isVideoOff = True
    join_param.isAudioOff = False

    meeting_service.Join(join_param)

    print("Bot is running. Press Ctrl+C to stop and generate report.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Bot stopping...")
    finally:
        print("Leaving meeting...")
        meeting_service.Leave(zmp.LEAVE_MEETING)
        time.sleep(2)
        zmp.DestroyMeetingService(meeting_service)
        zmp.DestroyAuthService(auth_service)
        zmp.CleanUPSDK()
        print("SDK cleaned up.")
        analyze_and_mark_attendance()

if __name__ == "__main__":
    main()