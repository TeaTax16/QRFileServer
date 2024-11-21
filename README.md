# FileServer
This project provides a simple and efficient file server that allows users to upload any file types and download them via QR codes. 
The application offers a user-friendly web interface for managing files, making it easy to share and access files within a local network.



## Features
- **Web Interface**: Users can upload any type of files and manage them through an intuitive web interface.
- **QR Code Download**: Generate QR codes for each file, enabling easy downloads by scanning the QR code with a device connected to the same network.
- **File Management**: View a list of all uploaded files and delete specific files as needed.
- **Drag and Drop Upload**: Easily upload files by dragging and dropping them onto the designated area on the home page.

## Pre-Requisites
 This system was developed using the following OS and software versions. other configurations may work, however only the following have been tested.
 - **Operating System**: ```Windows 11```
 - **Python**: [```3.12```](https://www.python.org/downloads/)

### Install Required Python Packages
```pip install flask qrcode[pil]```
- **Flask**: Web framework used for the web interface
- **qrcode**: Library for generating QR Codes

## Usage Instructions
### 1. Configure File Storage Folder

#### Application variables (```app.py```)
Edit the following variable in the script to specify your upload path.
```python
upload_folder = r'/directory/to/uploads'
```
```upload_folder``` = Path to the folder where the uploaded files will be stored.


### 2. Project structure
Project directory should be structured as follows:
```
project_folder/
├── app.py
├── templates/
│   ├── home.html
│   └── files.html
├── static/
│   ├── styles.css
│   └── logo.png (optional)
├── uploads/ (Automatically created if it doesn't exist)
```
- ```app.py```: The main Flask application script.
- ```templates/```: Directory containing HTML templates.
- ```static/```: Directory containing static files like CSS and images.
- ```uploads/```: Directory where the uploaded files are stored.


### 3. Running the Application
#### Start the Flask Application
- Open a terminal or command prompt.
- Navigate to the directory containing ```app.py```.
- Run the script:
```
python app.py
```
The Flask app will start running on ```http://localhost:8080/```.

### 4. Managing files
#### **Access the Home Page**
- Open a web browser and navigate to ```http://localhost:8080/```.
- 
#### **Uploading Files via Web Interface**
- **Drag and Drop**: Drag one or more files from your file explorer and drop them onto the designated dropzone area on the home page.
- **Click to Select**: Click on the dropzone area to open the file dialog, then select one or more files to upload.
- Files are uploaded automatically upon being dropped or selected, with feedback provided below the dropzone.

#### **Viewing and Managing Uploaded Files**
- From the home page, click on the **View QR Codes** button.
- Alternatively navigated directly to ```http://localhost:8080/files```
- The files page displays a list of all uploaded files
  - **File Name**:The name of the uploaded file.
  - **Show QR**: Button to generate and display a QR code for downloading the file.
  - **Delete**: Button to remove the specific file from the server.

#### **Generating QR Code for download**
- Click the **Show QR** button next to a file to generate its QR code.
- A modal will appear displaying the QR code.
- Scan the code with a device connected to the same network to download the files.

#### **Deleting Files**
- Click the **Delete** button next to a file to remove it from the server.
- A confirmation dialog will appear next to prevent accidental deletions. 

#### **Back to the Main Menu**
- From the files page, click the **Back to Main Menu** button to return to the home page.

![File Upload](https://github.com/user-attachments/assets/d3ec243f-2e28-474d-a4a7-1fd85946f2a5)


### 5. Stopping the Scripts
To stop the script and server, return to the  terminal window and press ```Ctrl+C```.


## Scripts Overview
### 1. ```app.py```
This script is the main Flask application. Main functionalities include:
- **File Upload**: Provides a web interface for users to upload any type of files.
- **File Listing**: Displays all uploaded files on the files page.
- **QR Code Generation**: Generates QR codes for each file, enabling easy downloads via scanning.
- **File Deletion**: Allows users to delete specific files from the server.
- **Flash Messaging**: Provides user feedback for actions like uploads and deletions.

### 2. Templates and Static Files
- **Templates:**
  - ```home.html```: The template for the home page, which includes file upload and status display.
  - ```files.html```: The template for the files page, which allows users to select and download files.
- **Static Files:**
  - ```styles.css```: Contains the CSS styles for the application.
  - ```logo.png```: Optional logo image displayed on the home page.

## Enhancements and Future Work
- **Authentication**: Implement user authentication for the web interface to restrict access.
- **PACS Server Integration**: Integrate the system with a PACS Server to securely retrieve medical images, ensuring compliance with medical regulations.