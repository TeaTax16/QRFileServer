import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import subprocess
import os

# Define paths to input folder, output folder, and 3D Slicer executable
input_folder = r'directory/to/input/folder'
output_folder = r'directory/to/output/folder'
slicer_path = r'directory/to/Slicer.exe'

# Custom event handler to check for changes in file directories
class NewFileHandler(FileSystemEventHandler):
    def __init__(self, folder_type):
        self.folder_type = folder_type

    # Method for when a new file is created in the watched directory
    def on_created(self, event):
        # Check that the created event is not a directory - it's a file
        if not event.is_directory:
            filepath = event.src_path  # Get full path of the file

            # Handle files from the input folder
            if self.folder_type == 'input':
                print(f'New file detected in input folder.\nSegmenting...\n')
                process_file(filepath)  # Call function to process the new file

            # Handle files from the output folder
            elif self.folder_type == 'output':
                print(f'New segmentation added to Output folder.')

# Function to run Slicer with the input file and output directory
def process_file(filepath):
    slicer_script = os.path.abspath(r'C:\Users\Takrim XARlabs\Documents\GitHub Projects\SlicerSegmentator\slicer_processing.py')
    subprocess.run([slicer_path, '--no-main-window', '--python-script', slicer_script, filepath, output_folder])

if __name__ == '__main__':
    # Initialise the event handler for both input and output folders
    input_event_handler = NewFileHandler('input')
    output_event_handler = NewFileHandler('output')

    # Initialise the observer
    observer = Observer()

    # Schedule the observer to watch the input folder for new files
    observer.schedule(input_event_handler, input_folder, recursive=False)
    # Schedule the observer to watch the output folder for new files
    observer.schedule(output_event_handler, output_folder, recursive=False)

    # Start the observer thread
    observer.start()
    print(f'Watching folders:\nInput folder: {input_folder},\nOutput folder: {output_folder},\nPress Ctrl+C to stop watching.\n')

    try:
        # Keep the script running to monitor events
        while True:
            time.sleep(1)  # 1-second pause between each loop
    # If user presses Ctrl+C, stop the observer
    except KeyboardInterrupt:
        observer.stop()

    observer.join()
