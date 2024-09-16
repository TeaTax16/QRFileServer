import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import subprocess
import os

# Define paths to input folder, output folder and 3D Slicer executable
input_folder = 'C:/Users/Takrim XARlabs/Documents/GitHub/SlicerSegmentator/Input'
output_folder = 'C:/Users/Takrim XARlabs/Documents/GitHub/SlicerSegmentator/Output'
slicer_path = 'C:/Users/Takrim XARlabs/AppData/Local/slicer.org/Slicer 5.6.2/Slicer.exe'

# Custom event handler to check for changes in a file directory
class NewFileHandler(FileSystemEventHandler):
    # Method for when a new file is created in the watched directory
    def on_created(self, event):
        # Check that the created event is not a directory- it's a file
        if not event.is_directory:
            filepath = event.src_path # Get full path of the file
            print(f'New File detected: {filepath}\n')
            process_file(filepath) # call function to process the new file


def process_file(filepath):
    print(f'Processing file...\n ')

if __name__ =='__main__':
    # Initialise the event handler
    event_handler= NewFileHandler()
    # Initialise the observer
    observer = Observer()
    # Schedule the observer to weatch the input folder for new files
    observer.schedule(event_handler, input_folder, recursive=False)
    # Start the observer thread
    observer.start()
    print(f'Watching folder: {input_folder} \nPress Ctrl+C to stop watching.')
    try:
        # Keep the script running to monitor events
        while True:
            time.sleep(1) # 1 second pause between each loop
    # If user presses Ctrl+C, stop the observer        
    except: KeyboardInterrupt: observer.stop() # type: ignore
    observer.join()