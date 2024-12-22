### **Updated README.md**

# QR Code Video Generator with YouTube Uploads

This script automates the generation of QR codes for YouTube links, uploads videos from Google Drive to YouTube, and arranges the QR codes in an A4-sized PDF. It includes support for stopping execution safely, resuming from the last saved state, and ensuring incremental progress is preserved.

---

## **Features**
1. **Video Uploads**: Uploads videos from a specified Google Drive folder to YouTube as unlisted videos.
2. **QR Code Generation**: Generates QR codes for the uploaded video links.
3. **PDF Output**: Arranges QR codes with captions in an A4-sized PDF.
4. **Progress Tracking**: Supports stop/resume functionality to prevent data loss during interruptions.

---

## **Prerequisites**

1. **Python Version**:
   - Ensure Python 3.7 or higher is installed.

2. **Dependencies**:
   - Install required libraries using:
     ```bash
     pip install qrcode[pil] google-api-python-client google-auth-oauthlib tqdm reportlab
     ```

3. **Google Cloud Projects**:
   - **Create two separate projects in Google Cloud Console**:
     - One for the **Google Drive API**.
     - Another for the **YouTube API**.

   - **Enable APIs**:
     - For the **Google Drive API**:
       Enable it using this [Google Drive API link](https://console.cloud.google.com/apis/library/drive.googleapis.com?inv=1&invt=Abkx9Q&project=unisonapp-ed905).
     - For the **YouTube API**:
       Enable it using this [YouTube API link](https://console.cloud.google.com/apis/library/youtube.googleapis.com?invt=Abkx9g&project=qr-code-445221).

   - **OAuth Credentials Setup**:
     - For the Google Drive project, configure `http://localhost:8001` as the redirect URI.
     - For the YouTube project, configure `http://localhost:8080` as the redirect URI.

4. **Secrets Files**:
   - Download the `client_secret.json` files for both projects and save them in the project directory:
     - Save the **Google Drive credentials** as `drive_client_secret.json`.
     - Save the **YouTube credentials** as `youtube_client_secret.json`.

---

## **Constants in the Code**

### **Editable Constants**
- `CSV_FILE`: The CSV file containing YouTube video titles and links. Default: `youtube_video_links.csv`.
- `QR_CODE_FOLDER`: Directory to save generated QR codes. Default: `qr_codes`.
- `OUTPUT_PDF`: Output PDF file containing QR codes. Default: `qr_code_sheet.pdf`.
- `TEMP_CSV_FILE`: Temporary file to store intermediate progress. Default: `temp_youtube_links.csv`.

### **Redirect URIs**
Ensure the following redirect URIs are set correctly:
- **Google Drive API Project**: `http://localhost:8001`
- **YouTube API Project**: `http://localhost:8080`

---

## **How to Use**

### **Setup**
1. Clone the repository:
   ```bash
   git clone <repository_url>
   cd <repository_folder>
   ```

2. Place the secret files in the directory:
   - `drive_client_secret.json`: For Google Drive API authentication.
   - `youtube_client_secret.json`: For YouTube API authentication.

### **Run the Script**
- **Fresh Start**:
  ```bash
  python <scriptName>.py
  ```
  This will delete any previous progress and start processing from scratch.

- **Resume Progress**:
  If the script was interrupted, use:
  ```bash
  python <scriptName>.py resume
  ```

### **Stop Command**
During execution, you can type `stop` to safely terminate the script. Progress will be saved, and you can resume later.

---

## **Output**

1. **QR Codes**:
   - Saved as PNG files in the `qr_codes` folder.

2. **CSV File**:
   - Contains video titles and corresponding YouTube links.
   - Example:
     ```csv
     Video Title,YouTube Link,QR Path
     example_video_1,https://www.youtube.com/watch?v=abc123,qr_codes/example_video_1.png
     example_video_2,https://www.youtube.com/watch?v=def456,qr_codes/example_video_2.png
     ```

3. **PDF File**:
   - Arranges all QR codes in an A4 layout with captions.
   - Default name: `qr_code_sheet.pdf`. The QR code output, the name is a bit long that's why it's not aligned
   ![](/screenshot.png)


---

## **Troubleshooting**

### **Common Issues**
1. **Invalid Secrets File**:
   - Ensure both `drive_client_secret.json` and `youtube_client_secret.json` are in the project directory.

2. **API Not Enabled**:
   - Enable the relevant APIs for your projects:
     - **Google Drive API**: [Enable Here](https://console.cloud.google.com/apis/library/drive.googleapis.com?inv=1&invt=Abkx9Q&project=unisonapp-ed905).
     - **YouTube API**: [Enable Here](https://console.cloud.google.com/apis/library/youtube.googleapis.com?invt=Abkx9g&project=qr-code-445221).

3. **Redirect URI Mismatch**:
   - Verify that the redirect URIs match the ones configured in the Google Cloud Console:
     - **Drive API**: `http://localhost:8001`
     - **YouTube API**: `http://localhost:8080`

4. **No Videos Found**:
   - Ensure the Google Drive folder ID is correct and contains video files.

5. **Dependency Errors**:
   - Reinstall dependencies using:
     ```bash
     pip install --force-reinstall qrcode[pil] google-api-python-client google-auth-oauthlib tqdm reportlab
     ```

---

## **Customization**

### **PDF Layout**
- Modify the cell size and spacing in the `create_pdf_with_qr_codes` function:
  - `cell_width`, `cell_height`: Size of each QR code cell.
  - `qr_size`: Size of the QR code itself.
  - `x_margin`, `y_margin`: Margins for the A4 layout.

### **Output Directories**
- Change `QR_CODE_FOLDER` and `OUTPUT_PDF` constants to set custom locations.

---

## **Contributing**
Feel free to submit issues or pull requests to enhance this script.

---

## **License**
This project is licensed under the MIT License.