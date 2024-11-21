from flask import Flask, send_from_directory, jsonify, request, redirect, url_for, render_template, flash
import os
from werkzeug.utils import secure_filename
import qrcode
import io
import base64
import socket

# Path to the uploads folder
upload_folder = r'directory\to\uploads'

# Ensure the uploads folder exists
os.makedirs(upload_folder, exist_ok=True)

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Needed for flashing messages

# Function to get the local network IP address of the host
def get_local_ip():
    hostname = socket.gethostname()
    try:
        return socket.gethostbyname(hostname)
    except socket.gaierror:
        return None

# Route to the home page (upload page)
@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        # Check if the POST request has the file part
        if 'file[]' not in request.files:
            response = {'status': 'error', 'message': 'No file part in the request.'}
            return jsonify(response), 400

        # Retrieve list of files
        files = request.files.getlist('file[]')

        # Validate and save the files
        if not files or all(file.filename == '' for file in files):
            response = {'status': 'error', 'message': 'No files selected for uploading.'}
            return jsonify(response), 400

        uploaded_filenames = []
        for file in files:
            if file and file.filename != '':
                filename = secure_filename(file.filename)
                filepath = os.path.join(upload_folder, filename)
                file.save(filepath)
                uploaded_filenames.append(filename)

        if uploaded_filenames:
            message = f'Uploaded {len(uploaded_filenames)} file(s) successfully!'
            # If the request is AJAX, return JSON
            if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                response = {'status': 'success', 'message': message, 'filenames': uploaded_filenames}
                return jsonify(response), 200
            else:
                flash(message, 'success')
                return redirect(url_for('home'))
        else:
            response = {'status': 'error', 'message': 'No valid files were uploaded.'}
            return jsonify(response), 400

    # For GET request, simply render the home page
    return render_template('home.html')

# Route to list all files in the server as a JSON
@app.route('/jsonlist', methods=['GET'])
def json_list():
    list_files = os.listdir(upload_folder)
    return jsonify(list_files)

# Route to download a specific file from the server
@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    filename = secure_filename(filename)
    return send_from_directory(upload_folder, filename, as_attachment=True)

# Route to generate a QR code for file download
@app.route('/qr', methods=['GET'])
def qr_code():
    filename = request.args.get('filename')
    if not filename:
        return "Error: No filename provided.", 400

    # Validate filename to prevent directory traversal
    filename = secure_filename(filename)
    file_path = os.path.join(upload_folder, filename)
    if not os.path.exists(file_path):
        return "Error: File does not exist.", 404

    # Get the local IP address
    local_ip = get_local_ip()
    if not local_ip:
        return "Error: Could not determine local IP address.", 500

    # Generate the download URL using the local IP and port 8080
    download_url = f"http://{local_ip}:8080/download/{filename}"
    img = qrcode.make(download_url)
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    return jsonify({'qr_code': img_base64})

# Route to list files with individual QR code generation and search functionality
@app.route('/files', methods=['GET'])
def files():
    # Get the search query from the URL parameters
    query = request.args.get('query', '').strip().lower()
    all_files = os.listdir(upload_folder)

    if query:
        # Filter files that contain the query string (case-insensitive)
        filtered_files = [f for f in all_files if query in f.lower()]
    else:
        filtered_files = all_files

    return render_template('files.html', files=filtered_files, query=request.args.get('query', ''))

# Route to delete a specific file
@app.route('/delete/<filename>', methods=['POST'])
def delete_file(filename):
    filename = secure_filename(filename)
    file_path = os.path.join(upload_folder, filename)
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
            flash(f'File "{filename}" has been deleted successfully.', 'success')
        except Exception as e:
            flash(f'Error deleting file "{filename}": {str(e)}', 'danger')
    else:
        flash(f'File "{filename}" does not exist.', 'warning')
    return redirect(url_for('files'))

# Start the Flask app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, ssl_context='adhoc')
