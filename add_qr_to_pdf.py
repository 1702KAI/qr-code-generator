import os
import csv
import qrcode
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor, white
import sys
import threading
from tqdm import tqdm

# Constants
CSV_FILE = "youtube_video_links.csv"
QR_CODE_FOLDER = "qr_codes"
OUTPUT_PDF = "qr_code_sheet.pdf"
TEMP_CSV_FILE = "temp_youtube_links.csv"
CUSTOM_COLOR = HexColor("#0F225D")
STOP_SCRIPT = False

# Ensure required directories exist
os.makedirs(QR_CODE_FOLDER, exist_ok=True)

# QR Code Generation
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

# PDF Generation
def create_pdf_with_qr_codes(qr_code_data):
    """Generate a PDF with QR codes arranged in an A4 layout."""
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

    for index, (video_title, qr_path) in enumerate(qr_code_data):
        col = index % columns
        row = (index // columns) % rows
        if row == 0 and col == 0 and index != 0:
            c.showPage()

        x = x_start + col * (cell_width + column_spacing)
        y = y_start - row * (cell_height + row_spacing)

        c.setFillColor(CUSTOM_COLOR)
        c.rect(x, y - cell_height, cell_width, cell_height, fill=True, stroke=False)

        qr_x = x + (cell_width - qr_size) / 2
        qr_y = y - cell_height / 1.5
        c.drawImage(qr_path, qr_x, qr_y, qr_size, qr_size)

        title_line1 = f"Hey {video_title},"
        title_line2 = "Scan me :)"

        c.setFillColor(white)
        c.setFont("Helvetica-Bold", 10)
        text_y_position_line1 = qr_y - 0.2 * inch
        text_y_position_line2 = text_y_position_line1 - 0.15 * inch

        c.drawCentredString(x + cell_width / 2, text_y_position_line1, title_line1)
        c.drawCentredString(x + cell_width / 2, text_y_position_line2, title_line2)

    c.save()

# Save and Load Progress
def save_progress(qr_code_data):
    """Save progress to a temporary CSV file."""
    with open(TEMP_CSV_FILE, 'w', newline='') as temp_file:
        fieldnames = ['Video Title', 'YouTube Link', 'QR Path']
        writer = csv.DictWriter(temp_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(qr_code_data)

def load_progress():
    """Load progress from a temporary CSV file."""
    if os.path.exists(TEMP_CSV_FILE):
        with open(TEMP_CSV_FILE, 'r') as temp_file:
            reader = csv.DictReader(temp_file)
            return list(reader)
    return []

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
def process_csv_and_generate_qr(resume=False):
    """Process CSV to generate QR codes and a PDF, with resume and stop functionality."""
    global STOP_SCRIPT

    if not os.path.exists(CSV_FILE):
        print(f"CSV file '{CSV_FILE}' not found.")
        return

    saved_progress = load_progress() if resume else []
    processed_titles = {entry['Video Title'] for entry in saved_progress}
    qr_code_data = saved_progress

    with open(CSV_FILE, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        rows = list(reader)

    remaining_rows = [row for row in rows if row['Video Title'] not in processed_titles]
    progress_bar = tqdm(total=len(rows), initial=len(saved_progress), desc="Processing QR Codes")

    for row in remaining_rows:
        if STOP_SCRIPT:
            break
        
        video_title = row['Video Title']
        video_url = row['YouTube Link']

        try:
            qr_path = generate_qr_code(video_title, video_url)
            qr_code_data.append({'Video Title': video_title, 'YouTube Link': video_url, 'QR Path': qr_path})
            save_progress(qr_code_data)
            progress_bar.update(1)
        except Exception as e:
            tqdm.write(f"Error processing {video_title}: {e}")

    progress_bar.close()

    if not STOP_SCRIPT:
        create_pdf_with_qr_codes([(entry['Video Title'], entry['QR Path']) for entry in qr_code_data])
        os.remove(TEMP_CSV_FILE)
        print(f"Process completed. PDF saved as '{OUTPUT_PDF}'.")
    else:
        print("Process stopped by user.")

# Main Execution
if __name__ == "__main__":
    stop_thread = threading.Thread(target=monitor_stop_command)
    stop_thread.daemon = True
    stop_thread.start()

    resume = len(sys.argv) > 1 and sys.argv[1].lower() == "resume"
    process_csv_and_generate_qr(resume=resume)
