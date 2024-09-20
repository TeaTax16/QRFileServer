from flask import Flask, send_from_directory, jsonify, request, redirect, url_for, render_template_string
import os
from werkzeug.utils import secure_filename
import threading
import queue
import subprocess
import time

app = Flask(__name__)

# Paths to the input and output folders
# input_folder = r'directory/to/input/folder'
# output_folder = r'directory/to/output/folder'
# slicer_path = r'directory/to/Slicer.exe'

input_folder = r'C:\Users\Takrim XARlabs\Documents\Auto Segment Test\Input'
output_folder = r'C:\Users\Takrim XARlabs\Documents\Auto Segment Test\Output'
slicer_path = r'C:\Users\Takrim XARlabs\AppData\Local\slicer.org\Slicer 5.6.2\Slicer.exe'

# Ensure the input and output folders exist
os.makedirs(input_folder, exist_ok=True)
os.makedirs(output_folder, exist_ok=True)

# Allowed file extensions
ALLOWED_EXTENSIONS = {'nrrd', 'nii', 'nii.gz', 'dcm', 'dicom'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Initialize queue and status variables
file_queue = queue.Queue()
new_files_list = []
currently_processing = None
status_lock = threading.Lock()  # lock to synchronize status updates

# Function to run 3D Slicer with the medical image input
def process_file(filepath):
    slicer_script = os.path.abspath(r'.\slicer_processing.py')
    subprocess.run([slicer_path, '--no-main-window', '--python-script', slicer_script, filepath, output_folder])

# Thread function to process files from the queue
def process_queue():
    global currently_processing
    while True:
        filepath = file_queue.get()
        filename = os.path.basename(filepath)
        with status_lock:
            currently_processing = filename
            if filename in new_files_list:
                new_files_list.remove(filename)
        # Process the file
        process_file(filepath)
        # After processing, reset currently processing file and delete the input file
        with status_lock:
            currently_processing = None
            os.remove(filepath)
        file_queue.task_done()

# Start the processing thread
processing_thread = threading.Thread(target=process_queue, daemon=True)
processing_thread.start()

# App route to upload files
@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    global new_files_list
    if request.method == 'POST':
        # Check if the POST request has the file part
        if 'file[]' not in request.files:
            return 'No file part in the request', 400
        # Retrieve list of files
        files = request.files.getlist('file[]')
        # Validate the files
        if not files or files[0].filename == '':
            return 'No selected files', 400

        uploaded_filenames = []
        for file in files:
            if file.filename == '':
                continue  # Skip empty filenames
            if file and allowed_file(file.filename):
                # Securely save the file to the input folder
                filename = secure_filename(file.filename)
                filepath = os.path.join(input_folder, filename)
                file.save(filepath)
                uploaded_filenames.append(filename)
                # Add the file to the processing queue
                file_queue.put(filepath)
                with status_lock:
                    new_files_list.append(filename)
            else:
                return f'File type not allowed: {file.filename}', 400

        if uploaded_filenames:
            return redirect(url_for('upload_file', success=True))
        else:
            return 'No valid files uploaded', 400
    else:
        # Render the upload form and status
        success = request.args.get('success')
        with status_lock:
            new_files = ', '.join(new_files_list) if new_files_list else 'Waiting for new files...'
            current_file = currently_processing if currently_processing else 'None'
            queue_size = file_queue.qsize()
        return render_template_string('''
            <!doctype html>
            <title>Upload New Files</title>
            <h1>Upload New Medical Images</h1>
            {% if success %}
            <p style="color: green;">Files uploaded successfully!</p>
            {% endif %}
            <form method=post enctype=multipart/form-data>
              <input type=file name="file[]" multiple accept=".nrrd,.nii,.nii.gz,.dcm,.dicom">
              <input type=submit value=Upload>
            </form>
            <hr>
            <h2>Processing Status</h2>
            <p><strong>New files added:</strong> {{ new_files }}</p>
            <p><strong>Currently Processing:</strong> {{ current_file }}</p>
            <p><strong>Files in the queue:</strong> {{ queue_size }}</p>
            ''', success=success, new_files=new_files, current_file=current_file, queue_size=queue_size)

# App route to list all files in the server as a JSON
@app.route('/files', methods=['GET'])
def list_files():
    files = os.listdir(output_folder)
    return jsonify(files)

# App route to download a specific file from the server
@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    return send_from_directory(output_folder, filename, as_attachment=True)

# Start the Flask app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
