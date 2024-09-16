# SlicerSegmentator
 This project provides a Python script that monitors a specified folder for new medical imaging files, processes them using 3D Slicers, Total Segmentator extension, and exports the resulting segmentation to a .gltf file using the OpenAnatomy Export extension. This output files are saved in a designated output folder.

## Features
- **Automated Folder Monitoring**: Continuousl watches a specified input folder for new files
- **3D Segmentation**: Uses the TotalSegmentator extension to segment medical imaging data
- **Export to GLFT**: Converts the segmentation output to ```.gltf``` format using the OpenAnatomy extension
- **Automated Workflow**: Processes new files automatically without manual intervention

## Pre-Requisites
 This system was developed using the following OS and software versions.
 - **Operating System**: ```Windows```
 - **Python**: [```3.12```](https://www.python.org/downloads/)
 - **3D Slicer**: [```5.6.2```](https://download.slicer.org/)
 
 Other configurations may work, however only the above have been tested.

### Install Required Python Packages
#### Watchdog
```bash
pip install watchdog
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
Modify the ```watch_folder.py``` script to define the paths for your input and output folders. This can be done by editing the following variables in the script:
```python
input_folder = 'path_to_your_input_folder'
output_folder = 'path_to_your_output_folder'
```
### 2. Running the Script
- Open a terminal or command prompt
- Navigate to the directory containing the script
- Run the python script
```
python watch_folder.py
```
### 3. File Monitoring
- The script will start monitoring the specific input folder for new files.
- When new medical imaging data is detected (must be compatible with 3D Slicer), the script will automatically trigger segmentation in 3D Slicer.
- After segmentation, the resulting data will be converted to ```.gltf``` format and saved in the specified output folder. 

For compatible 3D Slicer data check their [documentation](https://slicer.readthedocs.io/en/latest/user_guide/data_loading_and_saving.html)
