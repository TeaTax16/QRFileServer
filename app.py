import os
import sys
import base64
import random
import string
import socket
import threading
import io

from flask import (
    Flask,
    send_from_directory,
    jsonify,
    request,
    redirect,
    url_for,
    render_template,
    flash
)
from werkzeug.utils import secure_filename
import qrcode
import webview

# Configuration Constants
SECRET_KEY = 'your_secret_key'  # Replace with a secure key in production
UPLOAD_FOLDER_NAME = 'uploads'
FLASK_HOST = '0.0.0.0'
FLASK_PORT = 8080

def resource_path(relative_path):
    """
    Get absolute path to resource, works for dev and for PyInstaller.
    """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# Determine the base path based on execution context
if getattr(sys, 'frozen', False):
    # Running as a bundled executable
    app_base_path = os.path.dirname(sys.executable)
else:
    # Running as a standard script
    app_base_path = os.path.abspath(".")

# Setup upload folder
UPLOAD_FOLDER = os.path.join(app_base_path, UPLOAD_FOLDER_NAME)
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize Flask app
app = Flask(
    __name__,
    template_folder=resource_path('templates'),
    static_folder=resource_path('static')
)
app.config['SECRET_KEY'] = SECRET_KEY
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# In-memory storage for remote rooms
remote_rooms = {}

def get_local_ip():
    """
    Retrieve the local network IP address.
    """
    hostname = socket.gethostname()
    try:
        return socket.gethostbyname(hostname)
    except socket.gaierror:
        return None

def start_flask():
    """
    Start the Flask application.
    """
    app.run(host=FLASK_HOST, port=FLASK_PORT)

# =======================
# Flask App Routes
# =======================

@app.route('/', methods=['GET', 'POST'])
def home():
    """
    Home page that handles file uploads.
    """
    if request.method == 'POST':
        if 'file[]' not in request.files:
            response = {'status': 'error', 'message': 'No file part in the request.'}
            return jsonify(response), 400

        files = request.files.getlist('file[]')
        if not files or all(file.filename == '' for file in files):
            response = {'status': 'error', 'message': 'No files selected for uploading.'}
            return jsonify(response), 400

        uploaded_filenames = []
        for file in files:
            if file and file.filename:
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                uploaded_filenames.append(filename)

        if uploaded_filenames:
            message = f'Uploaded {len(uploaded_filenames)} file(s) successfully!'
            if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                response = {
                    'status': 'success',
                    'message': message,
                    'filenames': uploaded_filenames
                }
                return jsonify(response), 200
            else:
                flash(message, 'success')
                return redirect(url_for('home'))
        else:
            response = {'status': 'error', 'message': 'No valid files were uploaded.'}
            return jsonify(response), 400

    return render_template('home.html')

@app.route('/files', methods=['GET'])
def files():
    """
    Display a list of uploaded files with search functionality.
    """
    query = request.args.get('query', '').strip().lower()
    all_files = os.listdir(app.config['UPLOAD_FOLDER'])
    if query:
        filtered_files = [f for f in all_files if query in f.lower()]
    else:
        filtered_files = all_files
    return render_template('files.html', files=filtered_files, query=request.args.get('query', ''))

@app.route('/qr', methods=['GET'])
def qr_code():
    """
    Generate a QR code for downloading a specific file.
    """
    filename = request.args.get('filename')
    if not filename:
        return "Error: No filename provided.", 400

    filename = secure_filename(filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if not os.path.exists(file_path):
        return "Error: File does not exist.", 404

    local_ip = get_local_ip()
    if not local_ip:
        return "Error: Could not determine local IP address.", 500

    download_url = f"http://{local_ip}:{FLASK_PORT}/download/{filename}"
    img = qrcode.make(download_url)
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    return jsonify({'qr_code': img_base64})

@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    """
    Serve a file for download.
    """
    filename = secure_filename(filename)
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

@app.route('/delete/<filename>', methods=['POST'])
def delete_file(filename):
    """
    Delete a specified file.
    """
    filename = secure_filename(filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
            flash(f'File "{filename}" has been deleted successfully.', 'success')
        except Exception as e:
            flash(f'Error deleting file "{filename}": {str(e)}', 'danger')
    else:
        flash(f'File "{filename}" does not exist.', 'warning')
    return redirect(url_for('files'))

@app.route('/remote', methods=['GET'])
def remote_room():
    """
    Create a new remote room with unique codes and QR codes.
    """
    # Generate a random 6-character alphanumeric code
    code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

    # Initialize room information
    remote_rooms[code] = {
        'host_url': None,
        'clients_url': None
    }

    # Define role-specific codes
    host_code = f"{code}/h"
    client_code = f"{code}/c"

    # Encode codes using URL-safe Base64 without padding
    encoded_host = base64.urlsafe_b64encode(host_code.encode()).decode().rstrip('=')
    encoded_client = base64.urlsafe_b64encode(client_code.encode()).decode().rstrip('=')

    # Generate simxar URLs
    host_url = f"simxar://{encoded_host}"
    clients_url = f"simxar://{encoded_client}"

    # Update room information
    remote_rooms[code]['host_url'] = host_url
    remote_rooms[code]['clients_url'] = clients_url

    # Create QR codes for the simxar URLs
    host_qr = qrcode.make(host_url)
    clients_qr = qrcode.make(clients_url)

    # Convert QR codes to Base64 for embedding in HTML
    buffer_host = io.BytesIO()
    host_qr.save(buffer_host, format='PNG')
    host_qr_base64 = base64.b64encode(buffer_host.getvalue()).decode('utf-8')

    buffer_clients = io.BytesIO()
    clients_qr.save(buffer_clients, format='PNG')
    clients_qr_base64 = base64.b64encode(buffer_clients.getvalue()).decode('utf-8')

    return render_template(
        'remote.html',
        code=code,
        host_qr=host_qr_base64,
        clients_qr=clients_qr_base64
    )

# =======================
# Application Entry Point
# =======================

if __name__ == '__main__':
    flask_thread = threading.Thread(target=start_flask)
    flask_thread.daemon = True
    flask_thread.start()

    local_ip = get_local_ip()
    if not local_ip:
        print("Error: Could not determine local IP address.")
        sys.exit(1)
    else:
        window_title = "XARhub"
        window_url = f"http://{local_ip}:{FLASK_PORT}/"
        webview.create_window(
            window_title,
            window_url,
            confirm_close=True
        )
        webview.start()
