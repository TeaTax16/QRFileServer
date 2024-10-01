import sys
import os
import slicer  # type: ignore
from TotalSegmentator import TotalSegmentatorLogic  # type: ignore
from OpenAnatomyExport import OpenAnatomyExportLogic  # type: ignore

def main():
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

    # Create a new segmentation node
    segmentVolumeNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLSegmentationNode")
    segmentVolumeNode.SetName(base_filename)

    # Initialize TotalSegmentatorLogic for segmentation
    totalSegmentatorLogic = TotalSegmentatorLogic()
    totalSegmentatorLogic.process(
        inputVolume=loadedNode, # Input volume to segment
        outputSegmentation=segmentVolumeNode, # Output segmentation node
        task='total', # Segmentation task
        fast=False, # Detail level
    )

    # Initialize OpenAnatomyExportLogic for exporting to glTF
    OAExportLogic = OpenAnatomyExportLogic()
    shNode = slicer.vtkMRMLSubjectHierarchyNode.GetSubjectHierarchyNode(slicer.mrmlScene)
    inputItem = shNode.GetItemByDataNode(segmentVolumeNode)
    OAExportLogic.exportModel(
        inputItem=inputItem, # Segmentation Item to convert
        outputFolder=output_folder, # Output folder
        reductionFactor=0.01, # Mesh simplification factor
        outputFormat='glTF' # Export format
    )

    # Export the segmentation node with colour information as .seg.nrrd
    segmentation_filepath = os.path.join(output_folder, base_filename + ".seg.nrrd")
    success_seg = slicer.util.saveNode(segmentVolumeNode, segmentation_filepath)
    if not success_seg:
        print("Failed to save segmentation node to:", segmentation_filepath)
        sys.exit(1)
    else:
        print("Segmentation node saved successfully to:", segmentation_filepath)

    # Optional: Clean up the scene to free memory
    slicer.mrmlScene.Clear(0)
    sys.exit(0)

if __name__ == "__main__":
    main()