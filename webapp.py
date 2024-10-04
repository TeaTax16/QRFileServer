from flask import Flask, send_from_directory, jsonify, request, redirect, url_for, render_template_string, make_response
import os
from werkzeug.utils import secure_filename
import threading
import queue
import subprocess
import time
import qrcode
import io
import base64

# Paths to the input and output folders and the Slicer executable
input_folder = r'directory/to/input/folder'
output_folder = r'directory/to/output/folder'
slicer_path = r'directory/to/Slicer.exe'

# Ensure the input and output folders exist
os.makedirs(input_folder, exist_ok=True)
os.makedirs(output_folder, exist_ok=True)

# Initialise required variables
ALLOWED_EXTENSIONS = {'nrrd', 'nii', 'nii.gz', 'dcm', 'dicom'} # list of allowed filetypes
app = Flask(__name__) # create instance of the Flask web app
file_queue = queue.Queue() # file processing queue
new_files_list = [] # added files list
currently_processing = None # varible for currently processing file
status_lock = threading.Lock()  # lock to synchronize status updates

# Check for allowed filetypes
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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
            return redirect(url_for('upload_file', success=True))
        elif not error_message:
            error_message = 'No valid files uploaded'

    else:
        success = request.args.get('success')
    
    # Render the upload form and status
    with status_lock:
        new_files = ', '.join(new_files_list) if new_files_list else 'Waiting for new files...'
        current_file = currently_processing if currently_processing else 'None'
        queue_size = file_queue.qsize()

    # Adding Bootstrap for styling and enhancing the layout
    return render_template_string('''
    <!doctype html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
        <title>AutomatedSlicerSegmentator</title>
        <!-- Bootstrap CSS -->
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body class="bg-light">
        <div class="container">
            <div class="py-5 text-center">
                <h1>Automated Slicer Segmentator </h1>
                {% if success %}
                <div class="alert alert-success alert-dismissible fade show" role="alert">
                    Files uploaded successfully!
                    <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
                </div>
                {% endif %}
                {% if error_message %}
                <div class="alert alert-danger alert-dismissible fade show" role="alert">
                    {{ error_message }}
                    <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
                </div>
                {% endif %}
            </div>

            <!-- File upload form -->
            <div class="card p-4 mb-4">
                <form method="post" enctype="multipart/form-data" class="mb-3">
                    <div class="mb-3">
                        <label for="fileInput" class="form-label"><strong>Choose files to upload</strong> (multiple allowed):</label>
                        <input type="file" name="file[]" id="fileInput" class="form-control" multiple accept=".nrrd,.nii,.nii.gz,.dcm,.dicom">
                    </div>
                    <!-- Centering the button -->
                    <div class="text-center">
                        <button type="submit" class="btn btn-primary">Upload</button>
                    </div>
                </form>
            </div>

            <hr>

            <div class="card p-4">
                <h2>Processing Status</h2>
                <ul class="list-group">
                    <li class="list-group-item d-flex justify-content-between align-items-center">
                        <strong>Queue:</strong>
                        <span id="new_files">{{ new_files }}</span>
                    </li>
                    <li class="list-group-item d-flex justify-content-between align-items-center">
                        <strong>Processing:</strong>
                        <span id="current_file">{{ current_file }}</span>
                    </li>
                    <li class="list-group-item d-flex justify-content-between align-items-center">
                        <strong>Files Left:</strong>
                        <span id="queue_size">{{ queue_size }}</span>
                    </li>
                </ul>

                <div class="text-center mt-4">
                    <!-- Add the Refresh Button at the bottom of the processing status -->
                    <a href="/upload" class="btn btn-secondary">Refresh Page</a>
                    <!-- Add the button to open the JSON list in a new tab -->
                    <a href="/jsonlist" class="btn btn-info" target="_blank">Open JSON List</a>
                    <!-- Add the button to navigate to the files page -->
                    <a href="/files" class="btn btn-warning">Download Files with QR Code</a>
                </div>
            </div>

        </div>

        <!-- Bootstrap JS and dependencies -->
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/js/bootstrap.bundle.min.js"></script>
        <script>
            function updateStatus() {
                fetch('/status')
                    .then(response => response.json())
                    .then(data => {
                        document.getElementById('new_files').innerText = data.new_files;
                        document.getElementById('current_file').innerText = data.current_file;
                        document.getElementById('queue_size').innerText = data.queue_size;
                    })
                    .catch(error => console.error('Error fetching status:', error));
            }

            // Update status every 5 seconds
            setInterval(updateStatus, 5000);
            // Update status on page load
            updateStatus();
        </script>
    </body>
    </html>
''', success=request.args.get('success'), error_message=error_message, new_files=new_files, current_file=current_file, queue_size=queue_size)

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
    list = os.listdir(output_folder)
    return jsonify(list)

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

    download_url = url_for('download_file', filename=filename, _external=True)
    img = qrcode.make(download_url)
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    return jsonify({'qr_code': img_base64})

# App route to list files with a download button and QR code generation
@app.route('/files', methods=['GET'])
def files():
    files = os.listdir(output_folder)
    file_links = []
    for filename in files:
        download_url = url_for('download_file', filename=filename)
        qr_url = url_for('qr_code', filename=filename)
        file_links.append({'filename': filename, 'download_url': download_url, 'qr_url': qr_url})

    return render_template_string('''
    <!doctype html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
        <title>Available Files</title>
        <!-- Bootstrap CSS -->
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body class="bg-light">
        <div class="container">
            <div class="py-5 text-center">
                <h1>Available Files for Download</h1>
            </div>

            <div class="card p-4">
                <h2>Files List</h2>
                <ul class="list-group">
                    {% for file in file_links %}
                    <li class="list-group-item d-flex justify-content-between align-items-center">
                        <span>{{ file.filename }}</span>
                        <div>
                            <a href="{{ file.download_url }}" class="btn btn-primary me-2">Download</a>
                            <button class="btn btn-secondary" onclick="showQRCode('{{ file.qr_url }}')">Show QR Code</button>
                        </div>
                    </li>
                    {% endfor %}
                </ul>
            </div>

            <!-- QR Code Modal -->
            <div class="modal fade" id="qrCodeModal" tabindex="-1" aria-labelledby="qrCodeModalLabel" aria-hidden="true">
                <div class="modal-dialog">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title" id="qrCodeModalLabel">QR Code</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                        </div>
                        <div class="modal-body text-center">
                            <img id="qrCodeImage" src="" alt="QR Code">
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Bootstrap JS and dependencies -->
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/js/bootstrap.bundle.min.js"></script>
        <script>
            function showQRCode(qrUrl) {
                fetch(qrUrl)
                    .then(response => response.json())
                    .then(data => {
                        const qrCodeImage = document.getElementById('qrCodeImage');
                        qrCodeImage.src = 'data:image/png;base64,' + data.qr_code;
                        const qrCodeModal = new bootstrap.Modal(document.getElementById('qrCodeModal'));
                        qrCodeModal.show();
                    })
                    .catch(error => console.error('Error fetching QR code:', error));
            }
        </script>
    </body>
    </html>
    ''', file_links=file_links)

# Start the Flask app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)