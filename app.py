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
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Get the local network IP address
get_local_ip = lambda: socket.gethostbyname(socket.gethostname())

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        files = request.files.getlist('file[]')
        if not files or all(file.filename == '' for file in files):
            return jsonify({'status': 'error', 'message': 'No files selected for uploading.'}), 400

        uploaded_filenames = []
        for file in files:
            if file.filename:
                filename = secure_filename(file.filename)
                file.save(os.path.join(UPLOAD_FOLDER, filename))
                uploaded_filenames.append(filename)

        if uploaded_filenames:
            message = f'Uploaded {len(uploaded_filenames)} file(s) successfully!'
            if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'status': 'success', 'message': message, 'filenames': uploaded_filenames}), 200
            flash(message, 'success')
            return redirect(url_for('home'))
    return render_template('home.html')

@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    return send_from_directory(UPLOAD_FOLDER, secure_filename(filename), as_attachment=True)

@app.route('/qr', methods=['GET'])
def qr_code():
    filename = secure_filename(request.args.get('filename', ''))
    if not filename or not os.path.exists(os.path.join(UPLOAD_FOLDER, filename)):
        return "Error: File does not exist.", 404

    download_url = f"http://{get_local_ip()}:8080/download/{filename}"
    img = qrcode.make(download_url)
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    return jsonify({'qr_code': img_base64})

@app.route('/files', methods=['GET'])
def files():
    query = request.args.get('query', '').strip().lower()
    all_files = os.listdir(UPLOAD_FOLDER)
    filtered_files = [f for f in all_files if query in f.lower()] if query else all_files
    return render_template('files.html', files=filtered_files, query=query)

@app.route('/delete/<filename>', methods=['POST'])
def delete_file(filename):
    filename = secure_filename(filename)
    file_path = os.path.join(UPLOAD_FOLDER, filename)
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
    app.run(host='0.0.0.0', port=8080)

if __name__ == '__main__':
    threading.Thread(target=start_flask, daemon=True).start()
    webview.create_window("XARhub", f"http://{get_local_ip()}:8080/", confirm_close=True)
    webview.start()
