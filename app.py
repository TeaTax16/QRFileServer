import threading
from flask import Flask, send_from_directory, jsonify, request, redirect, url_for, render_template, flash
import os
from werkzeug.utils import secure_filename
import qrcode
import io
import base64
import socket
import webview

# Path to the uploads folder
upload_folder = r'uploads'

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

# Flask routes (unchanged, as per your initial script)
@app.route('/', methods=['GET', 'POST'])
def home():
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
            if file and file.filename != '':
                filename = secure_filename(file.filename)
                filepath = os.path.join(upload_folder, filename)
                file.save(filepath)
                uploaded_filenames.append(filename)
        if uploaded_filenames:
            message = f'Uploaded {len(uploaded_filenames)} file(s) successfully!'
            if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                response = {'status': 'success', 'message': message, 'filenames': uploaded_filenames}
                return jsonify(response), 200
            else:
                flash(message, 'success')
                return redirect(url_for('home'))
        else:
            response = {'status': 'error', 'message': 'No valid files were uploaded.'}
            return jsonify(response), 400
    return render_template('home.html')

# Additional routes (unchanged from your script)
@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    filename = secure_filename(filename)
    return send_from_directory(upload_folder, filename, as_attachment=True)

@app.route('/qr', methods=['GET'])
def qr_code():
    filename = request.args.get('filename')
    if not filename:
        return "Error: No filename provided.", 400
    filename = secure_filename(filename)
    file_path = os.path.join(upload_folder, filename)
    if not os.path.exists(file_path):
        return "Error: File does not exist.", 404
    local_ip = get_local_ip()
    if not local_ip:
        return "Error: Could not determine local IP address.", 500
    download_url = f"https://{local_ip}:8080/download/{filename}"
    img = qrcode.make(download_url)
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    return jsonify({'qr_code': img_base64})

@app.route('/files', methods=['GET'])
def files():
    query = request.args.get('query', '').strip().lower()
    all_files = os.listdir(upload_folder)
    if query:
        filtered_files = [f for f in all_files if query in f.lower()]
    else:
        filtered_files = all_files
    return render_template('files.html', files=filtered_files, query=request.args.get('query', ''))

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

# Function to run Flask in a separate thread
def start_flask():
    app.run(host='0.0.0.0', port=8080, ssl_context='adhoc')

# Main entry point
if __name__ == '__main__':
    flask_thread = threading.Thread(target=start_flask)
    flask_thread.daemon = True
    flask_thread.start()

    # Open the web app in a PyWebView window (using https)
    webview.create_window(
        "XARhub",
        "https://127.0.0.1:8080",
        confirm_close=True
    )
    webview.start()
