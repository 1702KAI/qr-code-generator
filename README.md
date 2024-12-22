# **QR Code Generator for Personalized Video Messages**

This repository offers versatile and cost-effective solutions for managing and generating QR codes linked to personalized video messages. Whether you're preparing for a team event, a corporate workshop, or a personalized marketing campaign, these tools make it incredibly easy to create custom stickers or share personalized content in bulk. 

You can choose between generating QR codes for videos stored in Google Drive or uploading them to YouTube as unlisted videos—allowing flexibility to match your preferences and audience. 

---

## **Repository Overview**

This repository contains three branches, each catering to specific needs:

1. **`main`**: The primary branch with an overview of the project and links to feature-specific branches.
2. **`bulk-upload-youtube-qr`**: Automates uploading videos to YouTube, generating QR codes, and handling interruptions gracefully.
3. **`generate-qr-code-drive`**: Focuses on generating QR codes for pre-existing YouTube links or Google Drive videos and organizing them into printable PDF sheets.

---

## **Branches**

### **1. `bulk-upload-youtube-qr`**
- **Purpose**: Ideal for uploading videos to YouTube (as unlisted or public), generating QR codes, and sharing them with ease.
- **Why Use This?**
  - Simplifies sharing links without requiring public access to Google Drive.
  - Useful if you want the video to be on YouTube but hidden from public search (unlisted).
- **Key Features**:
  - Downloads videos from Google Drive.
  - Uploads videos to YouTube with customizable titles and privacy settings.
  - Generates QR codes for the uploaded videos.
  - Allows resuming interrupted processes and stopping safely.
- **Run Instructions**:
  1. Clone the branch:
     ```bash
     git clone -b bulk-upload-youtube-qr <repository_url>
     cd bulk-upload-youtube-qr
     ```
  2. Install dependencies:
     ```bash
     pip install -r requirements.txt
     ```
  3. Enable APIs:
     - [Enable Google Drive API](https://console.cloud.google.com/apis/library/drive.googleapis.com?project=<project-id>)
     - [Enable YouTube API](https://console.cloud.google.com/apis/library/youtube.googleapis.com?project=<project-id>)
  4. Configure:
     - Use two separate Google Cloud projects (one for Drive API, one for YouTube API).
     - Set up OAuth credentials for each and use unique redirect URIs.
  5. Run the script:
     ```bash
     python upload_videos_and_generate_qr.py
     ```
  6. Resume (if needed):
     ```bash
     python upload_videos_and_generate_qr.py resume
     ```

---

### **2. `generate-qr-code-drive`**
- **Purpose**: Quickly generate printable QR codes for pre-existing video links from Google Drive or YouTube.
- **Why Use This?**
  - Avoids the hassle of uploading videos or managing YouTube accounts.
  - Perfect if your videos are already public or shared via a Drive link.
- **Key Features**:
  - Generates QR codes for video links in bulk.
  - Organizes QR codes into a neat PDF layout for printing.
  - Includes resume and stop functionalities to handle interruptions.
- **Run Instructions**:
  1. Clone the branch:
     ```bash
     git clone -b generate-qr-code-drive <repository_url>
     cd generate-qr-code-drive
     ```
  2. Install dependencies:
     ```bash
     pip install -r requirements.txt
     ```
  3. Input CSV File:
     - Ensure a file named `youtube_video_links.csv` with columns `Video Title` and `YouTube Link` exists in the directory.
  4. Run the script:
     ```bash
     python generate_qr_and_pdf.py
     ```
  5. Resume (if needed):
     ```bash
     python generate_qr_and_pdf.py resume
     ```

---

## **Why This Repository?**

This project is perfect for both personal and professional use:
- **For Events**: Print QR code stickers in bulk to send personalized video messages to attendees.
- **For Teams**: Create and share instructional videos or greetings without requiring public YouTube listings.
- **For Flexibility**: 
  - Use **Google Drive links** to avoid hassle.
  - Publish videos as **unlisted YouTube links** for seamless sharing without requiring login.

---

## **Setup and Configuration**

### **API Requirements**
1. **Google Drive API**:
   - Enable [Google Drive API](https://console.cloud.google.com/apis/library/drive.googleapis.com).
2. **YouTube API**:
   - Enable [YouTube API](https://console.cloud.google.com/apis/library/youtube.googleapis.com).

---

## **Sample Outputs**

### **QR Code Stickers**
- Print-ready PDF with captions like:
  ```text
  Hey [Video Title],
  Scan me :)
  ```

### **CSV File**
- Tracks video links and QR code paths for reference.

### **Screenshots**
- Check `screenshots/` for visual examples of QR codes and printable PDFs.

---

## **How to Choose the Right Branch**

- **Choose `bulk-upload-youtube-qr`** if:
  - You want to upload videos to YouTube.
  - You need QR codes for unlisted YouTube videos.

- **Choose `generate-qr-code-drive`** if:
  - You already have YouTube or Drive links.
  - You want quick and printable QR codes.

---

## **Contributing**

We welcome contributions! Open issues, suggest features, or submit pull requests to enhance this project.

---

## **License**

This project is licensed under the MIT License. 🎉