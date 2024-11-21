from flask import Flask, send_from_directory, jsonify, request, redirect, url_for, render_template, flash
import os
from werkzeug.utils import secure_filename
import qrcode
import io
import base64
import socket

# Path to the uploads folder
upload_folder = r'C:\Users\Takrim XARlabs\Documents\My Scripts\SegTest\FilesStorage'

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
    error_message = None  # Initialize error message
    if request.method == 'POST':
        # Check if the POST request has the file part
        if 'file[]' not in request.files:
            error_message = 'No file part in the request'
        else:
            # Retrieve list of files
            files = request.files.getlist('file[]')
            # Validate and save the files
            if not files or files[0].filename == '':
                error_message = 'No selected files'
            else:
                uploaded_filenames = []
                for file in files:
                    if file.filename == '':
                        continue  # Skip empty filenames
                    filename = secure_filename(file.filename)
                    filepath = os.path.join(upload_folder, filename)
                    file.save(filepath)
                    uploaded_filenames.append(filename)
                if uploaded_filenames:
                    flash('Files uploaded successfully!', 'success')
                    return redirect(url_for('home'))
                else:
                    error_message = 'No valid files uploaded'
    else:
        success = request.args.get('success')

    # Render the home template
    return render_template('home.html',
                           success=success,
                           error_message=error_message)

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
        return "Error: No filename provided", 400

    # Validate filename to prevent directory traversal
    filename = secure_filename(filename)
    file_path = os.path.join(upload_folder, filename)
    if not os.path.exists(file_path):
        return "Error: File does not exist", 404

    # Get the local IP address
    local_ip = get_local_ip()
    if not local_ip:
        return "Error: Could not determine local IP address", 500

    # Generate the download URL using the local IP and port 8080
    download_url = f"http://{local_ip}:8080/download/{filename}"
    img = qrcode.make(download_url)
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    return jsonify({'qr_code': img_base64})

# Route to list files with individual QR code generation
@app.route('/files', methods=['GET'])
def files():
    error_message = None
    # For GET request, simply list the files
    files = os.listdir(upload_folder)
    return render_template('files.html', files=files, error_message=error_message)

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
    app.run(host='0.0.0.0', port=8080)
