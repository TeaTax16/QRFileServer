from flask import Flask, send_from_directory, jsonify, request, redirect, url_for, render_template
import os
from werkzeug.utils import secure_filename
import threading
import queue
import subprocess
import qrcode
import io
import base64
import socket

# Paths to the input and output folders and the Slicer executable
input_folder = r'directory/to/input/folder'
output_folder = r'C:\Users\Takrim XARlabs\Documents\My Scripts\SegTest\Output'
slicer_path = r'directory/to/Slicer.exe'

# Ensure the input and output folders exist
os.makedirs(input_folder, exist_ok=True)
os.makedirs(output_folder, exist_ok=True)

# Initialise required variables
ALLOWED_EXTENSIONS = {'nrrd', 'nii', 'nii.gz', 'dcm', 'dicom'}  # list of allowed filetypes
app = Flask(__name__)  # create instance of the Flask web app
file_queue = queue.Queue()  # file processing queue
new_files_list = []  # added files list
currently_processing = None  # variable for currently processing file
status_lock = threading.Lock()  # lock to synchronize status updates

# Get the local network IP address of the host.
def get_local_ip():
    hostname = socket.gethostname()
    try:
        return socket.gethostbyname(hostname)
    except socket.gaierror:
        return None

# Check for allowed filetypes
def allowed_file(filename):
    return '.' in filename and \
        (filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS or
         filename.lower().endswith('.nii.gz'))

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

# App route to the home page (upload page)
@app.route('/', methods=['GET', 'POST'])
def home():
    global new_files_list
    error_message = None  # Initialize error message
    if request.method == 'POST':
        # Check if the POST request has the file part
        if 'file[]' not in request.files:
            error_message = 'No file part in the request'
        else:
            # Retrieve list of files
            files = request.files.getlist('file[]')
            # Validate the files
            if not files or files[0].filename == '':
                error_message = 'No selected files'
            else:
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
                        error_message = f'File type not allowed: {file.filename}'
                        break

            if not error_message and uploaded_filenames:
                return redirect(url_for('home', success=True))
            elif not error_message:
                error_message = 'No valid files uploaded'

    else:
        success = request.args.get('success')

    # Render the home page and status
    with status_lock:
        new_files = ', '.join(new_files_list) if new_files_list else 'Waiting for new files...'
        current_file = currently_processing if currently_processing else 'None'
        queue_size = file_queue.qsize()

    # Render the home template
    return render_template('home.html',
                           success=request.args.get('success'),
                           error_message=error_message,
                           new_files=new_files,
                           current_file=current_file,
                           queue_size=queue_size)

# App route to provide status updates in JSON format
@app.route('/status')
def status():
    with status_lock:
        new_files = ', '.join(new_files_list) if new_files_list else 'Waiting for new files...'
        current_file = currently_processing if currently_processing else 'None'
        queue_size = file_queue.qsize()
    return jsonify({
        'new_files': new_files,
        'current_file': current_file,
        'queue_size': queue_size
    })

# App route to list all files in the server as a JSON
@app.route('/jsonlist', methods=['GET'])
def json_list():
    list_files = os.listdir(output_folder)
    return jsonify(list_files)

# App route to download a specific file from the server
@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    return send_from_directory(output_folder, filename, as_attachment=True)

# App route to generate a QR code for file download
@app.route('/qr', methods=['GET'])
def qr_code():
    filename = request.args.get('filename')
    if not filename:
        return "Error: No filename provided", 400

    # Validate filename to prevent directory traversal
    filename = secure_filename(filename)
    file_path = os.path.join(output_folder, filename)
    if not os.path.exists(file_path):
        return "Error: File does not exist", 404

    # Get the local IP address
    local_ip = get_local_ip()
    if not local_ip:
        return "Error: Could not determine local IP address", 500

    # Generate the download URL using the local IP
    download_url = f"http://{local_ip}:8080/download/{filename}"
    img = qrcode.make(download_url)
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    return jsonify({'qr_code': img_base64})

# App route to list files with individual QR code generation
@app.route('/files', methods=['GET'])
def files():
    error_message = None
    # For GET request, simply list the files
    files = os.listdir(output_folder)
    return render_template('files.html', files=files, error_message=error_message)

# Start the Flask app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
