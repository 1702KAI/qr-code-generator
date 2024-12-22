import os
import csv
import qrcode
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
import threading
import sys
from tqdm import tqdm

# Constants
DRIVE_SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
QR_CODE_FOLDER = "qr_codes"
CSV_FILE = "drive_video_links.csv"
TEMP_CSV_FILE = "temp_drive_video_links.csv"

# Placeholder for sensitive data
CLIENT_SECRET_FILE = "path_to_your_client_secret.json"  # Replace with the actual path to your client_secret.json file
FOLDER_ID = "your_google_drive_folder_id"  # Replace with your Google Drive folder ID

# Global variable for stop functionality
stop_script = False

# Ensure required directories exist
os.makedirs(QR_CODE_FOLDER, exist_ok=True)

# Authenticate and return Google Drive service instance
def authenticate_google_drive():
    """Authenticate and initialize Google Drive API."""
    flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, DRIVE_SCOPES)
    credentials = flow.run_local_server(port=8080)
    return build('drive', 'v3', credentials=credentials)

# Generate a QR code and save it as a PNG file
def create_qr_code(video_title, video_url):
    """Generate a QR code for the provided video URL."""
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

# Save progress to a temporary CSV file
def save_progress(video_links):
    """Save the current progress to a temporary CSV file."""
    with open(TEMP_CSV_FILE, 'w', newline='') as temp_csvfile:
        fieldnames = ['Video Title', 'Google Drive Link']
        writer = csv.DictWriter(temp_csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(video_links)

# Load saved progress from the temporary CSV file
def load_progress():
    """Load previously saved progress from the temporary CSV file."""
    if os.path.exists(TEMP_CSV_FILE):
        with open(TEMP_CSV_FILE, 'r') as temp_csvfile:
            reader = csv.DictReader(temp_csvfile)
            return list(reader)
    return []

# Monitor user input to allow stopping the script
def monitor_stop_command():
    """Monitor for 'stop' command to terminate the script gracefully."""
    global stop_script
    while True:
        command = input()
        if command.strip().lower() == "stop":
            stop_script = True
            print("\nStopping execution... Progress will be saved.\n")
            break

# Process videos from Google Drive and generate QR codes
def process_videos_from_drive(folder_id, resume=False):
    """Process videos from Google Drive, generating QR codes and saving progress."""
    global stop_script

    # Authenticate Google Drive
    drive_service = authenticate_google_drive()

    # Fetch video files from the specified folder
    query = f"'{folder_id}' in parents and mimeType contains 'video/'"
    results = drive_service.files().list(q=query, fields="files(id, name)").execute()
    items = results.get('files', [])

    if not items:
        print("No videos found in the specified Google Drive folder.")
        return

    # Load progress if resuming
    saved_progress = load_progress() if resume else []
    processed_titles = {entry['Video Title'] for entry in saved_progress}
    video_links = saved_progress
    remaining_items = [item for item in items if item['name'] not in processed_titles]

    print(f"Total videos: {len(items)} | Remaining: {len(remaining_items)}")
    print("Type 'stop' anytime to gracefully exit and save progress.\n")

    # Initialize progress bar
    progress_bar = tqdm(total=len(items), initial=len(saved_progress), desc="Processing Videos", ncols=100)

    for item in remaining_items:
        if stop_script:
            break  # Stop processing if 'stop' command is received

        file_id = item['id']
        video_title = item['name']
        video_url = f"https://drive.google.com/file/d/{file_id}/view"

        try:
            # Generate QR code and save progress
            qr_path = create_qr_code(video_title, video_url)
            video_links.append({'Video Title': video_title, 'Google Drive Link': video_url})
            save_progress(video_links)
            progress_bar.update(1)
        except Exception as e:
            tqdm.write(f"Error processing {video_title}: {e}")

    progress_bar.close()

    # Save final progress and clean up temporary file
    if not stop_script:
        save_final_csv(video_links)
        if os.path.exists(TEMP_CSV_FILE):
            os.remove(TEMP_CSV_FILE)

    print("Process completed." if not stop_script else "Process stopped by user.")

# Save the final progress to the main CSV file
def save_final_csv(video_links):
    """Save all processed video links to the main CSV file."""
    with open(CSV_FILE, 'w', newline='') as csvfile:
        fieldnames = ['Video Title', 'Google Drive Link']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(video_links)

# Entry point
if __name__ == "__main__":
    # Check for 'resume' argument
    resume = len(sys.argv) > 1 and sys.argv[1].lower() == "resume"

    # Start thread to monitor for 'stop' command
    stop_thread = threading.Thread(target=monitor_stop_command)
    stop_thread.daemon = True  # Daemon thread terminates with the main program
    stop_thread.start()

    # Process videos
    process_videos_from_drive(FOLDER_ID, resume=resume)
