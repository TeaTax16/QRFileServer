import sys
import os
import slicer # type: ignore
from TotalSegmentator import TotalSegmentatorLogic # type: ignore
from OpenAnatomyExport import OpenAnatomyExportLogic # type: ignore

def main():
    # Get the input arguments
    input_filepath = sys.argv[1]
    output_folder = sys.argv[2]

    # Load the input file
    print(f'Loading file: {input_filepath}')
    loadedNode = slicer.util.loadVolume(input_filepath)

    # Check if the volume was loaded
    if not loadedNode:
        print('Failed to load volume.')
        sys.exit(1)

    # Run Total Segmentator
    print('Running Total Segmentator...')
    # Create a new segmentation node in Slicer's MRML scene for output
    segmentVolumeNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLSegmentationNode")

    # Initialise TotalSegmentatorLogic to process the segmentation
    totalSegmentatorLogic = TotalSegmentatorLogic()
    totalSegmentatorLogic.process(
        inputVolume=loadedNode, # Input volume to be segmented
        outputSegmentation=segmentVolumeNode,   # Output Segmentation Node
        task='total',   # Segmentation task
        fast=True,  # Detail of the segmentation task
    )

    # Export to .gltf 
    print('Exporting to .gltf...')
    # Initialize the logic
    OAExportLogic = OpenAnatomyExportLogic()
    # Get tge subject hierarchy node
    shNode = slicer.vtkMRMLSubjectHierarchyNode.GetSubjectHierarchyNode(slicer.mrmlScene)
    # Retrieve the corresponding segmentation node
    inputItem = shNode.GetItemByDataNode(segmentVolumeNode)
    # Export the segmentation model to the specified output folder
    OAExportLogic.exportModel(
    inputItem=inputItem,    # Segmentation Item to convert
    outputFolder=output_folder, # Output folder to export to
    outputFormat='glTF' # Format to export to
    
)

    print(f'Export complete. Files saved in: {output_folder}')
    slicer.mrmlScene.Clear(0)
    sys.exit(0)

if __name__ == "__main__":
    main()
