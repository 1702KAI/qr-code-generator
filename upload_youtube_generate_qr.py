import os
import csv
import qrcode
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
import sys
import threading
from tqdm import tqdm

# Constants
DRIVE_SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
YOUTUBE_SCOPES = ['https://www.googleapis.com/auth/youtube.upload']
QR_CODE_FOLDER = "qr_codes"
CSV_FILE = "youtube_video_links.csv"
TEMP_CSV_FILE = "temp_youtube_video_links.csv"
TEMP_DOWNLOAD_FOLDER = "temp_videos"
DRIVE_FOLDER_ID = "YOUR_GOOGLE_DRIVE_FOLDER_ID"  # Replace with your Google Drive folder ID
STOP_SCRIPT = False

# Ensure required directories exist
os.makedirs(QR_CODE_FOLDER, exist_ok=True)
os.makedirs(TEMP_DOWNLOAD_FOLDER, exist_ok=True)

# Authentication Functions
def authenticate_drive():
    """Authenticate and initialize the Google Drive API."""
    flow = InstalledAppFlow.from_client_secrets_file('drive_client_secret.json', DRIVE_SCOPES)
    credentials = flow.run_local_server(port=8001)
    return build('drive', 'v3', credentials=credentials)

def authenticate_youtube():
    """Authenticate and initialize the YouTube API."""
    flow = InstalledAppFlow.from_client_secrets_file('youtube_client_secret.json', YOUTUBE_SCOPES)
    credentials = flow.run_local_server(port=8080)
    return build('youtube', 'v3', credentials=credentials)

# QR Code Generation
def generate_qr_code(video_title, video_url):
    """Generate a QR code for the given video URL."""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4
    )
    qr.add_data(video_url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    qr_path = os.path.join(QR_CODE_FOLDER, f"{video_title}.png")
    img.save(qr_path)
    return qr_path

# File Handling
def save_progress(data):
    """Save progress to a temporary CSV file."""
    with open(TEMP_CSV_FILE, 'w', newline='') as temp_file:
        fieldnames = ['Video Title', 'YouTube Link', 'QR Path']
        writer = csv.DictWriter(temp_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)

def load_progress():
    """Load progress from a temporary CSV file."""
    if os.path.exists(TEMP_CSV_FILE):
        with open(TEMP_CSV_FILE, 'r') as temp_file:
            reader = csv.DictReader(temp_file)
            return list(reader)
    return []

def save_final_output(data):
    """Save final data to the main CSV file."""
    with open(CSV_FILE, 'w', newline='') as final_file:
        fieldnames = ['Video Title', 'YouTube Link', 'QR Path']
        writer = csv.DictWriter(final_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)

# Video Processing
def download_videos(drive_service):
    """Download videos from Google Drive."""
    query = f"'{DRIVE_FOLDER_ID}' in parents and mimeType contains 'video/'"
    results = drive_service.files().list(q=query, fields="files(id, name)").execute()
    items = results.get('files', [])
    
    if not items:
        print("No videos found in the Google Drive folder.")
        return []
    
    downloaded_files = []
    for item in items:
        file_id = item['id']
        file_name = item['name']
        file_path = os.path.join(TEMP_DOWNLOAD_FOLDER, file_name)

        try:
            request = drive_service.files().get_media(fileId=file_id)
            with open(file_path, 'wb') as file:
                file.write(request.execute())
            downloaded_files.append(file_path)
            print(f"Downloaded: {file_name}")
        except Exception as e:
            print(f"Failed to download {file_name}: {e}")
    
    return downloaded_files

def upload_to_youtube(youtube_service, file_path, title):
    """Upload a video to YouTube."""
    body = {
        'snippet': {
            'title': title,
            'description': 'Uploaded via API',
            'tags': ['example', 'youtube', 'api'],
            'categoryId': '22'  # Category: People & Blogs
        },
        'status': {
            'privacyStatus': 'unlisted'
        }
    }
    try:
        media = MediaFileUpload(file_path, chunksize=-1, resumable=True)
        request = youtube_service.videos().insert(part="snippet,status", body=body, media_body=media)
        response = request.execute()
        video_id = response['id']
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        print(f"Uploaded to YouTube (Unlisted): {video_url}")
        return video_url
    except Exception as e:
        print(f"Failed to upload {title}: {e}")
        return None

# Monitor Stop Command
def monitor_stop_command():
    """Monitor for 'stop' command to terminate the script gracefully."""
    global STOP_SCRIPT
    while True:
        command = input()
        if command.strip().lower() == "stop":
            STOP_SCRIPT = True
            print("\nStopping execution... Progress will be saved.\n")
            break

# Main Processing Function
def process_videos(resume=False):
    """Main function to download, upload, and generate QR codes."""
    global STOP_SCRIPT

    drive_service = authenticate_drive()
    youtube_service = authenticate_youtube()

    saved_progress = load_progress() if resume else []
    processed_titles = {entry['Video Title'] for entry in saved_progress}
    data = saved_progress

    video_files = download_videos(drive_service)
    remaining_files = [file for file in video_files if os.path.basename(file).rsplit('.', 1)[0] not in processed_titles]

    progress_bar = tqdm(total=len(video_files), initial=len(saved_progress), desc="Processing Videos")

    for file_path in remaining_files:
        if STOP_SCRIPT:
            break
        
        video_title = os.path.basename(file_path).rsplit('.', 1)[0]
        youtube_url = upload_to_youtube(youtube_service, file_path, video_title)
        if youtube_url:
            qr_path = generate_qr_code(video_title, youtube_url)
            data.append({'Video Title': video_title, 'YouTube Link': youtube_url, 'QR Path': qr_path})
            save_progress(data)
            progress_bar.update(1)

    progress_bar.close()
    if not STOP_SCRIPT:
        save_final_output(data)
        if os.path.exists(TEMP_CSV_FILE):
            os.remove(TEMP_CSV_FILE)
    print("Process completed." if not STOP_SCRIPT else "Process stopped by user.")

# Main Execution
if __name__ == "__main__":
    stop_thread = threading.Thread(target=monitor_stop_command)
    stop_thread.daemon = True
    stop_thread.start()

    resume = len(sys.argv) > 1 and sys.argv[1].lower() == "resume"
    process_videos(resume=resume)
