# FileServer
This project provides and automated pipeline for processing medical imaging files using 3D Slicer. The pipeline includes:
- Using a web interface to upload medical imaging files.
- Automatically processing them using 3D Slicer's Total Segmentation extension.
- Exporting the resulting segmentation to a .gltf using the OpenAnatomy Export extension.
- Providing a web interface to view, select and download processed outputs via QR code.

## Features
- **Web Interface**: Users can upload medical imaging files and download processing files through a user-friendly web interface.
- **Queue Management**: Handles multiple files by queueing them and providing real-time status updates displaying files added, files in queue and files being processed.
- **3D Segmentation**: Uses the TotalSegmentator extension to segment medical imaging data.
- **Automated Cleanup**: Deletes input files after processing to manage disk space.
- **Export to GLFT**: Converts the segmentation output to ```.gltf``` format using the OpenAnatomy extension.
- **QR Code Download**: Users can select processed files and download them by scanning a generated QR code. 

## Pre-Requisites
 This system was developed using the following OS and software versions.
 - **Operating System**: ```Windows 11```
 - **Python**: [```3.12```](https://www.python.org/downloads/)
 - **3D Slicer**: [```5.6.2```](https://download.slicer.org/)
 
 Other configurations may work, however only the above have been tested.

### Install Required Python Packages
```pip install flask werkzeug qrcode[pil]```
- **Flask**: Web framework used for the web interface
- **Werkzeug**: Utility library used by Flask
- **qrcode**: Library for generating QR Codes

### Install 3D Slicer Extensions
#### Total Segmentator
- Open 3D Slicer
- Navigate to ```Extensions Manager```
- Search for ```Total Segmentator```
- Click ```Install```

#### OpenAnatomy Export
- Open 3D Slicer
- Navigate to ```Extensions Manager```
- Search for ```SlicerOpenAnatomy```
- Click ```Install```

## Usage Instructions
### 1. Configure Input and Output Folders
#### Application variables (```app.py```)
Edit the following variables in the script to specify your paths:
```python
input_folder = r'directory/to/input/folder'
output_folder = r'directory/to/output/folder'
slicer_path = r'directory/to/Slicer.exe'
```

- ```input_folder```: Path to the folder where the uploaded files will be stored.
- ```output_folder```: Path to the folder where the processed files will be stored.
- ```slicer_path```: Path to the 3D Slicer executable.


### 2. Project structure
Project directory should be structured as follows:
```angular2html
project_folder/
├── app.py
├── slicer_processing.py
├── templates/
│   ├── home.html
│   └── files.html
├── static/
│   ├── styles.css
│   └── logo.png (optional)
```
- ```app.py```: The main Flask application script.
- ```slicer_processing.py```: The script executed by 3D Slicer to process files.
- ```templates/```: Directory containing HTML templates.
- ```static/```: Directory containing static files like CSS and images.


### 3. Running the Application
#### Start the Flask Application
- Open a terminal or command prompt.
- Navigate to the directory containing ```app.py```.
- Run the script:
```
python app.py
```
The Flask app will start running on ```http://localhost:8080/```.

### 4. Processing files
#### **Uploading Files via Web Interface**
- Open a web browser and navigate to ```http://localhost:8080/upload```.
- Use the file selector to choose one or more medical imaging files to upload.
- Click **Upload**

Supported file types: ```.nrrd```, ```.nii```, ```.nii.gz```, ```.dcm```, ```.dicom```.

![File Upload](https://github.com/user-attachments/assets/d3ec243f-2e28-474d-a4a7-1fd85946f2a5)



#### **Monitoring Processing Status**
The home page also displays real-time status updates, including:
- **Queue**: Files waiting to be processed.
- **Processing**: Currently processing files.
- **Files left**: Number of files left in the queue

The status updates automatically ever few seconds.

![Processing Status](https://github.com/user-attachments/assets/cd1257de-ca20-4812-b45b-92268810fd67)



#### **Accessing Processed Files**
- **View available files**: Click on the ```Download Files``` button or navigate to ```http://localhost:8080/files```.
- **Selecting Files for Download**: 
  - On the files pages, select the files you wish to download by checking the corresponding check boxes
  - Click on ```Generate QR Code```
 ![Files List](https://github.com/user-attachments/assets/ab7a20bc-7b34-4110-a356-559b5e3d75f3)

- **Downloading via QR**:
  - A QR code will be displayed in a model window.
  - Scan the QR code with a device connected to the same network as the server.
 ![QR Code](https://github.com/user-attachments/assets/1f179c10-f95d-42f4-8b8e-a59b591c2597)


### 5. Stopping the Scripts
To stop the script and server, return to the  terminal window and press ```Ctrl+C```.

## Scripts Overview
### 1. ```app.py```
This script is the main Flask application. Main functionalities include:
- **File Upload**: Provides a web interface for users to upload medical imaging files.
- **Queue Management**: Manages the uploaded files using a queue and processes them in the background using threading.
- **Processing Workflow**:
  - Starts 3D Slicer in the background using ```subprocess```.
  - Runs the ```slicer_processing.py``` script within 3D Slicer to perform segmentation.
  - Deletes the input file after processing to manage disk space.
- **Real-Time Status Updates**: Provides real-time updates on processing status via web interface
- **File Download with QR Code**:
  - Lists processed files and allows users to select files for download.
  - Generates a zip archive of selected files.
  - Generated a QR code that links to the download URL for the zip file.
  - Deletes the zip file after download to manage disk space.

### 2. ```slicer_processing.py```
This script runs inside 3D Slicer and performs the following:
- Loads the input medical image.
- Runs Total Segmentator to segment the image.
- Exports the segmentations to a ```.gltf``` file using ```OpenAnatomy Export```.
- Saves the output in the specified output folder.

### 3. Templates and Static Files
- **Templates:**
  - ```home.html```: The template for the home page, which includes file upload and status display.
  - ```files.html```: The template for the files page, which allows users to select and download files.
- **Static Files:**
  - ```styles.css```: Contains the CSS styles for the application.
  - ```logo.png```: Optional logo image displayed on the home page

## Enhancements and Future Work
- **Authentication**: Implement user authentication for the web interface to restrict access
- **PACS Server Integration**: Integrate the system with a PACS Server to securely retrieve and store medical images, ensuring compliance with medical regulations.

## Acknowledgements
- **3D Slicer**: An open source software platform for medical image informatics, image processing, and three-dimensional visualisation.
- **Total Segmentator**: An extension for 3D Slicer that provides automated segmentation of medical images.
- **OpenAnatomy Export**: An extension for exporting anatomical models in various formats.
