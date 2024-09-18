import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import subprocess
import os
import threading
import queue
import sys

# Define paths to input folder, output folder, and 3D Slicer executable
input_folder = r'directory/to/input/folder'
output_folder = r'directory/to/output/folder'
slicer_path = r'directory/to/Slicer.exe'

# Queue to store files to be processed
file_queue = queue.Queue()
new_files_list = []
currently_processing = None
status_lock = threading.Lock() # lock to synchronise status updates

# Custom event handler to check for changes in file directories
class NewFileHandler(FileSystemEventHandler):
    def __init__(self, folder_type):
        self.folder_type = folder_type

    # Method for when a new file is created in the watched directory
    def on_created(self, event):
        # Check that the created event is not a directory - it's a file
        if not event.is_directory:
            filepath = event.src_path  # Get full path of the file
            filename = os.path.basename(filepath) # Get filename

            # Handle files from the input folder
            if self.folder_type == 'input':
                file_queue.put(filepath)
                with status_lock:
                    new_files_list.append(filename)

# Function to run Slicer with the input file and output directory
def process_file(filepath):
    slicer_script = os.path.abspath(r'.\slicer_processing.py')
    subprocess.run([slicer_path, '--no-main-window', '--python-script', slicer_script, filepath, output_folder])

# Thread function to process files from the queue
def process_queue():
    global currently_processing
    while True:
        # Retrieve next file in the queue
        filepath = file_queue.get()
        filename = os.path.basename(filepath)
        # Update currently processing file
        with status_lock:
            currently_processing = filename
            if filename in new_files_list:
                new_files_list.remove(filename)
        # Process the file
        process_file(filepath)
        
        # After processing, reset currently processing file and delete the input file
        with status_lock:
            currently_processing=None
            os.remove(filepath)
            
        # Indicate the task is done
        file_queue.task_done()

# Function to update console window output
def update_console_status():
    while True:
        with status_lock:
            # Clear the console 
            os.system('cls' if os.name =='nt' else 'clear')

            print(f"Upload new files to: {input_folder}\nPress Ctrl+C to stop program.\n-=-=-=-=-=-=-=-=-=-=-=-=-=-=-")

            # Print new files added
            if new_files_list:
                print(f'New files added: {", ".join(new_files_list)}')
            else:
                print("Waiting for new files...")

            # Print currently processing file
            if currently_processing:
                print(f'Currently Processing: {currently_processing}')
                # Print number of files in the queue
                queue_size = file_queue.qsize()
                print(f"Files in the queue: {queue_size}")
            else:
                print("")
            
        time.sleep(1)

if __name__ == '__main__':
    # Initialise the event handler for input folder
    input_event_handler = NewFileHandler('input')

    # Initialise the observer
    observer = Observer()

    # Schedule the observer to watch the input folder for new files
    observer.schedule(input_event_handler, input_folder, recursive=False)

    # Start the observer thread
    observer.start()

    #Start the processing thread
    processing_thread = threading.Thread(target=process_queue, daemon=True)
    processing_thread.start()

    # Start the console  update thread
    console_thread = threading.Thread(target=update_console_status, daemon=True)
    console_thread.start()

    try:
        # Keep the script running to monitor events
        while True:
            time.sleep(1)  # 1-second pause between each loop
    # If user presses Ctrl+C, stop the observer
    except KeyboardInterrupt:
        observer.stop()

    observer.join()