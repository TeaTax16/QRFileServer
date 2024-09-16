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