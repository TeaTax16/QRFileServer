import sys
import os
import json  # Importing json module for handling JSON operations
import slicer  # type: ignore
from TotalSegmentator import TotalSegmentatorLogic  # type: ignore
from OpenAnatomyExport import OpenAnatomyExportLogic  # type: ignore
import vtk  # Import VTK for handling VTK-specific operations
import zipfile  # Importing zipfile to handle the creation of zip archives

def main():
    # Ensure correct number of arguments
    if len(sys.argv) != 3:
        print("Usage: slicer_processing.py <input_filepath> <output_folder>")
        sys.exit(1)

    input_filepath = sys.argv[1]
    output_folder = sys.argv[2]

    # Validate input file
    if not os.path.isfile(input_filepath):
        print(f"Input file does not exist: {input_filepath}")
        sys.exit(1)

    # Ensure output folder exists
    os.makedirs(output_folder, exist_ok=True)

    # Extract base filename without extension
    input_filename = os.path.basename(input_filepath)
    base_filename, ext = os.path.splitext(input_filename)

    # Handle double extensions like .nii.gz or .nrrd
    if base_filename.endswith('.nii'):
        base_filename = base_filename[:-4]
        ext = '.nii.gz'
    elif base_filename.endswith('.nrrd'):
        base_filename = base_filename[:-5]
        ext = '.nrrd'

    # Load the input medical image
    loadedNode = slicer.util.loadVolume(input_filepath)

    # Check if the volume was loaded successfully
    if not loadedNode:
        print("Failed to load volume:", input_filepath)
        sys.exit(1)

    # *** Begin: Save Original Input as .nii.gz ***
    # Define the path for the original converted file
    original_nii_gz_filename = f"{base_filename}_original.nii.gz"
    original_nii_gz_filepath = os.path.join(output_folder, original_nii_gz_filename)

    # Save the loaded volume as .nii.gz
    success_original = slicer.util.saveNode(loadedNode, original_nii_gz_filepath)
    if not success_original:
        print(f"Failed to save original input as .nii.gz: {original_nii_gz_filepath}")
        sys.exit(1)
    else:
        print(f"Original input saved successfully as: {original_nii_gz_filepath}")
    # *** End: Save Original Input as .nii.gz ***

    # Create a new segmentation node
    segmentVolumeNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLSegmentationNode")
    segmentVolumeNode.SetName(base_filename)

    # Initialize TotalSegmentatorLogic for segmentation
    totalSegmentatorLogic = TotalSegmentatorLogic()
    totalSegmentatorLogic.process(
        inputVolume=loadedNode,  # Input volume to segment
        outputSegmentation=segmentVolumeNode,  # Output segmentation node
        task='total',  # Segmentation task
        fast=False,  # Detail level
    )

    # Initialize OpenAnatomyExportLogic for exporting to glTF
    OAExportLogic = OpenAnatomyExportLogic()
    shNode = slicer.vtkMRMLSubjectHierarchyNode.GetSubjectHierarchyNode(slicer.mrmlScene)
    inputItem = shNode.GetItemByDataNode(segmentVolumeNode)

    # Create a ZIP file containing all outputs
    zip_filepath = os.path.join(output_folder, base_filename + ".zip")
    zip_contents = []  # List to track contents of the zip file

    with zipfile.ZipFile(zip_filepath, 'w', compression=zipfile.ZIP_DEFLATED) as zipf:
        # *** Begin: Add Original .nii.gz to ZIP ***
        if os.path.exists(original_nii_gz_filepath):
            zipf.write(original_nii_gz_filepath, os.path.basename(original_nii_gz_filepath))
            zip_contents.append(os.path.basename(original_nii_gz_filepath))
            os.remove(original_nii_gz_filepath)  # Clean up the original converted file
            print(f"Added and removed original .nii.gz: {original_nii_gz_filepath}")
        # *** End: Add Original .nii.gz to ZIP ***

        # Export glTF directly to zip
        gltf_filepath = os.path.join(output_folder, base_filename + ".gltf")
        OAExportLogic.exportModel(
            inputItem=inputItem,                # Segmentation Item to convert
            outputFolder=output_folder,         # Output folder
            reductionFactor=0.01,               # Mesh simplification factor
            outputFormat='glTF'                 # Export format
        )
        if os.path.exists(gltf_filepath):
            zipf.write(gltf_filepath, os.path.basename(gltf_filepath))
            zip_contents.append(os.path.basename(gltf_filepath))
            os.remove(gltf_filepath)
            print(f"Added and removed glTF file: {gltf_filepath}")

        # Export the segmentation node to a labelmap volume node and add directly to zip
        labelmapVolumeNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLLabelMapVolumeNode")
        slicer.modules.segmentations.logic().ExportAllSegmentsToLabelmapNode(segmentVolumeNode, labelmapVolumeNode)
        labelmap_filepath = os.path.join(output_folder, base_filename + ".nii.gz")
        success_labelmap = slicer.util.saveNode(labelmapVolumeNode, labelmap_filepath)
        if not success_labelmap:
            print("Failed to save labelmap volume node to:", labelmap_filepath)
            sys.exit(1)
        else:
            zipf.write(labelmap_filepath, os.path.basename(labelmap_filepath))
            zip_contents.append(os.path.basename(labelmap_filepath))
            os.remove(labelmap_filepath)
            print(f"Added and removed labelmap .nii.gz: {labelmap_filepath}")

        # Create JSON Mapping of Segments and add directly to zip
        try:
            # Get the segmentation object
            segmentation = segmentVolumeNode.GetSegmentation()

            # Retrieve all segment IDs
            segmentIdList = vtk.vtkStringArray()
            segmentation.GetSegmentIDs(segmentIdList)

            # Initialize a dictionary to hold label value to segment name mapping
            segment_mapping = {}

            # Assume label values start from 1 and correspond to the order of segments
            for i in range(segmentIdList.GetNumberOfValues()):
                segment_id = segmentIdList.GetValue(i)
                segment = segmentation.GetSegment(segment_id)
                if not segment:
                    print(f"Warning: Segment ID {segment_id} could not be retrieved.")
                    continue

                segment_name = segment.GetName()
                label_value = i + 1  # Label values start from 1

                # Add the mapping to the dictionary
                segment_mapping[str(label_value)] = segment_name

            # Define the JSON file path
            json_filepath = os.path.join(output_folder, base_filename + ".json")

            # Write the mapping to the JSON file with indentation for readability
            with open(json_filepath, 'w') as json_file:
                json.dump(segment_mapping, json_file, indent=4)

            zipf.write(json_filepath, os.path.basename(json_filepath))
            zip_contents.append(os.path.basename(json_filepath))
            os.remove(json_filepath)
            print(f"Added and removed JSON mapping file: {json_filepath}")

            print("Segment mapping JSON saved successfully to:", json_filepath)

        except Exception as e:
            print("Failed to create segment mapping JSON:", str(e))
            sys.exit(1)

    print("All outputs have been zipped successfully to:", zip_filepath)

    # *** Begin: Add Contents JSON to ZIP ***
    contents_json_filepath = os.path.join(output_folder, f"{base_filename}_contents.json")
    with open(contents_json_filepath, 'w') as contents_json_file:
        json.dump(zip_contents, contents_json_file, indent=4)

    zipf.write(contents_json_filepath, os.path.basename(contents_json_filepath))
    zip_contents.append(os.path.basename(contents_json_filepath))
    os.remove(contents_json_filepath)
    print("Contents JSON saved and added to ZIP:", contents_json_filepath)
    # *** End: Add Contents JSON to ZIP ***

    # Clean up the scene to free memory
    slicer.mrmlScene.Clear(0)
    sys.exit(0)

if __name__ == "__main__":
    main()
