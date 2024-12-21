### **README.md**

```markdown
# QR Code Video Generator

This project automates the generation of QR codes for video links stored in a Google Drive folder. It also saves the video details to a CSV file.

## Prerequisites

1. **Python**:
   - Ensure Python 3.7 or higher is installed.

2. **Dependencies**:
   - Install the required Python packages using pip:
     ```bash
     pip install qrcode[pil] google-api-python-client google-auth-oauthlib
     ```

3. **Google Cloud Project**:
   - Set up a Google Cloud project to enable the Google Drive API.

## Setting Up the Secrets

1. **Google Drive Folder ID**:
   - Locate the folder in your Google Drive.
   - Copy the folder ID from the URL (e.g., `https://drive.google.com/drive/folders/<FOLDER_ID>`).

2. **OAuth2 Credentials File (`client_secret.json`)**:
   - Create OAuth 2.0 credentials in the Google Cloud Console:
     - Navigate to `APIs & Services > Credentials`.
     - Select `Create Credentials > OAuth client ID`.
     - Configure the consent screen and download the JSON file.
   - Save the file in the project directory as `client_secret.json`.

3. **Update Constants**:
   - Open the script and replace the placeholders:
     - Replace `YOUR_GOOGLE_DRIVE_FOLDER_ID` with your actual folder ID.
     - Ensure the `client_secret.json` file is in the same directory.

## Running the Script

1. Clone the repository:
   ```bash
   git clone <repository_url>
   cd <repository_folder>
   ```

2. Run the script:
   ```bash
   python <script_name>.py
   ```

## Output

1. **QR Codes**:
   - Generated QR codes are saved in the `qr_codes` directory.

2. **CSV File**:
   - The `drive_video_links.csv` file contains video titles and their Google Drive links.

## Troubleshooting

- **Missing `client_secret.json`**:
  Ensure you’ve downloaded and placed the OAuth2 credentials file correctly.

- **Permission Errors**:
  Check the Google Cloud project settings to ensure the Drive API is enabled.

- **No Videos Found**:
  Verify the folder ID and that the folder contains video files.

## Contributing

Feel free to contribute by opening issues or submitting pull requests.

## License

This project is licensed under the MIT License.
```
