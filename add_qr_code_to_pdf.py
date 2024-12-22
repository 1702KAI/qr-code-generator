import os
import csv
import qrcode
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from reportlab.lib.colors import HexColor, white
from tqdm import tqdm
import sys
import threading

# Constants
DRIVE_SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
QR_CODE_FOLDER = "qr_codes"
CSV_FILE = "drive_video_links.csv"
TEMP_CSV_FILE = "temp_drive_video_links.csv"
OUTPUT_PDF = "qr_code_sheet.pdf"
CLIENT_SECRET_FILE = "path_to_your_client_secret.json"  # Replace with the actual path to your client_secret.json file
FOLDER_ID = "your_google_drive_folder_id"  # Replace with your Google Drive folder ID
CUSTOM_COLOR = HexColor("#0F225D")
STOP_SCRIPT = False

# Ensure required directories exist
os.makedirs(QR_CODE_FOLDER, exist_ok=True)


# Authentication Functions
def authenticate_google_drive():
    """Authenticate and initialize the Google Drive API."""
    flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, DRIVE_SCOPES)
    credentials = flow.run_local_server(port=8080)
    return build('drive', 'v3', credentials=credentials)


# QR Code Functions
def generate_qr_code(video_title, video_url):
    """Generate a QR code for the given video URL and save it as a PNG file."""
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


def clean_filename(filename):
    """Extract and clean the name from the filename."""
    name_part = filename.rsplit('.', maxsplit=1)[0]
    return ''.join(filter(lambda x: not x.isdigit(), name_part)).strip()


# PDF Functions
def create_pdf_with_qr_codes(qr_code_data):
    """Generate a PDF with QR codes and their corresponding video titles."""
    c = canvas.Canvas(OUTPUT_PDF, pagesize=A4)
    width, height = A4
    x_margin, y_margin = 0.75 * inch, 0.75 * inch
    cell_width, cell_height = 1.5 * inch, 2 * inch
    qr_size = 1 * inch
    column_spacing, row_spacing = 0.1 * inch, 0.3 * inch

    columns = int((width - 2 * x_margin) / (cell_width + column_spacing))
    rows = int((height - 2 * y_margin) / (cell_height + row_spacing))

    x_start = x_margin
    y_start = height - y_margin

    for index, (filename, qr_path) in enumerate(qr_code_data):
        col = index % columns
        row = (index // columns) % rows
        if row == 0 and col == 0 and index != 0:
            c.showPage()

        x = x_start + col * (cell_width + column_spacing)
        y = y_start - row * (cell_height + row_spacing)

        # Draw background for the cell
        c.setFillColor(CUSTOM_COLOR)
        c.rect(x, y - cell_height, cell_width, cell_height, fill=True, stroke=False)

        # Center QR code in the cell
        qr_x = x + (cell_width - qr_size) / 2
        qr_y = y - cell_height / 1.5
        c.drawImage(qr_path, qr_x, qr_y, qr_size, qr_size)

        # Add titles below the QR code
        name = clean_filename(filename)
        c.setFillColor(white)
        c.setFont("Helvetica-Bold", 10)
        c.drawCentredString(x + cell_width / 2, qr_y - 0.2 * inch, f"Hey {name},")
        c.drawCentredString(x + cell_width / 2, qr_y - 0.35 * inch, "Scan me :)")

    c.save()


# Progress Management Functions
def save_progress(video_links):
    """Save the current progress to a temporary CSV file."""
    with open(TEMP_CSV_FILE, 'w', newline='') as csvfile:
        fieldnames = ['Video Title', 'Google Drive Link', 'QR Path']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(video_links)


def load_progress():
    """Load previously saved progress from the temporary CSV file."""
    if os.path.exists(TEMP_CSV_FILE):
        with open(TEMP_CSV_FILE, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            return list(reader)
    return []


# Stop Monitoring
def monitor_stop_command():
    """Monitor user input for the 'stop' command to terminate the script gracefully."""
    global STOP_SCRIPT
    while True:
        command = input()
        if command.strip().lower() == "stop":
            STOP_SCRIPT = True
            print("\nStopping execution... Progress will be saved.\n")
            break


# Video Processing
def process_drive_videos(resume=False):
    """Fetch videos from Google Drive, generate QR codes, and save progress."""
    global STOP_SCRIPT

    # Clear previous progress if not resuming
    if not resume:
        clear_previous_progress()

    drive_service = authenticate_google_drive()

    query = f"'{FOLDER_ID}' in parents and mimeType contains 'video/'"
    results = drive_service.files().list(q=query, fields="files(id, name)").execute()
    items = results.get('files', [])

    if not items:
        print("No videos found in the specified Google Drive folder.")
        return

    saved_progress = load_progress()
    processed_titles = {entry['Video Title'] for entry in saved_progress}
    video_links = saved_progress
    remaining_items = [item for item in items if item['name'] not in processed_titles]

    print(f"Total videos: {len(items)} | Remaining: {len(remaining_items)}")
    print("Type 'stop' anytime to gracefully exit and save progress.\n")

    progress_bar = tqdm(total=len(items), initial=len(saved_progress), desc="Processing Videos")

    for item in remaining_items:
        if STOP_SCRIPT:
            break

        file_id = item['id']
        video_title = item['name']
        video_url = f"https://drive.google.com/file/d/{file_id}/view"

        try:
            qr_path = generate_qr_code(video_title, video_url)
            video_links.append({'Video Title': video_title, 'Google Drive Link': video_url, 'QR Path': qr_path})
            save_progress(video_links)
            progress_bar.update(1)
        except Exception as e:
            print(f"Error processing {video_title}: {e}")

    progress_bar.close()

    if not STOP_SCRIPT:
        finalize_output(video_links)


def clear_previous_progress():
    """Clear previous progress files and directories."""
    if os.path.exists(TEMP_CSV_FILE):
        os.remove(TEMP_CSV_FILE)
    if os.path.exists(CSV_FILE):
        os.remove(CSV_FILE)
    for file in os.listdir(QR_CODE_FOLDER):
        os.remove(os.path.join(QR_CODE_FOLDER, file))
    print("Starting fresh...")


def finalize_output(video_links):
    """Finalize the output by saving to CSV and generating the PDF."""
    with open(CSV_FILE, 'w', newline='') as csvfile:
        fieldnames = ['Video Title', 'Google Drive Link', 'QR Path']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(video_links)

    create_pdf_with_qr_codes([(entry['Video Title'], entry['QR Path']) for entry in video_links])
    if os.path.exists(TEMP_CSV_FILE):
        os.remove(TEMP_CSV_FILE)


# Main Script Execution
if __name__ == "__main__":
    stop_thread = threading.Thread(target=monitor_stop_command)
    stop_thread.daemon = True
    stop_thread.start()

    if len(sys.argv) > 1 and sys.argv[1].lower() == "resume":
        process_drive_videos(resume=True)
    else:
        process_drive_videos(resume=False)
