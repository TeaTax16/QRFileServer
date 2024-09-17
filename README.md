# AutomatedSlicerSegmentator
 This project provides a Python script that monitors a specified folder for new medical imaging files, processes them using 3D Slicer's Total Segmentator extension, and exports the resulting segmentation to a ```.gltf``` file using the OpenAnatomy Export extension. These outputs are then available to access from a local web server.

## Features
- **Automated Folder Monitoring**: Continuously watches a specified input folder for new files.
- **3D Segmentation**: Uses the TotalSegmentator extension to segment medical imaging data.
- **Export to GLFT**: Converts the segmentation output to ```.gltf``` format using the OpenAnatomy extension.
- **Automated Workflow**: Processes new files automatically without manual intervention.
- **File Server for Output Files**: Provides a web interface to list and download processed files from the output folder.

## Pre-Requisites
 This system was developed using the following OS and software versions.
 - **Operating System**: ```Windows 11```
 - **Python**: [```3.12```](https://www.python.org/downloads/)
 - **3D Slicer**: [```5.6.2```](https://download.slicer.org/)
 
 Other configurations may work, however only the above have been tested.

### Install Required Python Packages
#### **Watchdog**: used for file monitoring
```
pip install watchdog
```

#### **Flask**: used for file server
```
pip install flask
```

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
#### Folder Monitoring Script (```watch_folder.py```)
Edit the following variables in the script to specify your paths:
```python
input_folder = r'directory/to/input/folder'
output_folder = r'directory/to/output/folder'
slicer_path = r'directory/to/Slicer.exe'
```
#### File Server Script (```fileserver.py```)
Set path to the output folder:
```python
output_folder = r'directory/to/output/folder'
```

### 2. Running the Scripts
#### Start the Folder Monitoring Script
- Open a terminal or command prompt.
- Navigate to the directory containing ```watch_folder.py```.
- Run the python script.
```
python watch_folder.py
```
#### Start the File Server Script
- Open a new termincal or command prompt (keeping the first running).
- Navigate to the directory containing  ```fileserver.py```.
- Run the python script.
```
python fileserver.py
```
The Flask app will start running on ```http://localhost:8080/```.

### 3. Processing files
#### Adding Files for Segmentation
- Place your medical imaging files (must be compatible with 3D Slicer) into the **input folder** you specified.
- The folder monitoring script will detect new files and automatically process them using 3D Slicer.
- After segmentation, the resulting ```.gltf``` files will be saved in the **output folder**.

For compatible 3D Slicer data check their [documentation](https://slicer.readthedocs.io/en/latest/user_guide/data_loading_and_saving.html).

#### Accessing Processed Files
- **List Files**: Open a web browser and navigate to ```http://localhost:8080/files``` to view a list of processed files.
- **Download a File**: Navigate to ```http://localhost:8080/download/<filename>```, replacing ```<filename>``` with the actual filename.

Example:
```
http://localhost:8080/download/segmented_model.gltf
```

### 4. Stopping the Scripts
To stop either the folder monitoring script or the Flask file server, return to the respective terminal window and press ```Ctrl+C```.

## Scripts Overview
### 1. ```watch_folder.py```
This script uses the ```watchdog``` library to monitor the input folder. When a new file is detected:
- It starts 3D Slicer in the background using ```subprocess```.
- Runs the ```slicer_processing.py``` script within 3D Slicer to perform segmentation.
- Exports the segmentation to a ```.gltf``` file in the output folder.

### 2. ```slicer_processing.py```
This script runs inside 3D Slicer and performs the following:
- Loads the input medical image.
- Runs Total Segmentator to segment the image.
- Exports the segmentations to a ```.gltf``` file using ```OpenAnatomy Export```.
- Saves the output in the specified output folder.

### 3. ```fileserver.py```
This Flask application provides a simple web interface to:
- **List Files**: provides a JSON list of all files in the output folder.
- **Download Files**: Allows users to download specific files from the output folder.