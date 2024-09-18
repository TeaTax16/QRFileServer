import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import subprocess
import os
import threading
import queue

# Define paths to input folder, output folder, and 3D Slicer executable
input_folder = r'directory/to/input/folder'
output_folder = r'directory/to/output/folder'
slicer_path = r'directory/to/Slicer.exe'

# Queue to store files to be processed
file_queue = queue.Queue()
new_files_list = []
new_files_lock = threading.Lock()

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
                with new_files_lock:
                    new_files_list.append(filename)
                    print(f'New Files added: {", ".join(new_files_list)}')


# Function to run Slicer with the input file and output directory
def process_file(filepath):
    slicer_script = os.path.abspath(r'.\slicer_processing.py')
    subprocess.run([slicer_path, '--no-main-window', '--python-script', slicer_script, filepath, output_folder])

# Thread function to process files from the queue
def process_queue():
    while True:
        # Retrieve new file in the queue
        filepath = file_queue.get()
        filename = os.path.basename(filepath)

        # Update number of files to process
        queue_size = file_queue.qsize()
        #Print currently processing file and the number of files left
        print(f'Currently processing {filename}\nFiles left to process: {queue_size}')

        # Process the file and output once completed
        process_file(filepath)
        print(f'{filename} has been segmented.')
        
        # Remove file from queue list
        with new_files_lock:
            if filename in new_files_list:
                new_files_list.remove(filename)
        # Indicate task is done
        file_queue.task_done()


if __name__ == '__main__':
    # Initialise the event handler for both input and output folders
    input_event_handler = NewFileHandler('input')

    # Initialise the observer
    observer = Observer()

    # Schedule the observer to watch the input folder for new files
    observer.schedule(input_event_handler, input_folder, recursive=False)


    # Start the observer thread
    observer.start()
    print(f'\nWatching folders:\nInput: {input_folder}\n\nPress Ctrl+C to stop watching.\n')

    #Start the processing thread
    processing_thread = threading.Thread(target=process_queue, daemon=True)
    processing_thread.start()

    try:
        # Keep the script running to monitor events
        while True:
            time.sleep(1)  # 1-second pause between each loop
    # If user presses Ctrl+C, stop the observer
    except KeyboardInterrupt:
        observer.stop()

    observer.join()
