# application/routes/files.py

import os
from flask import (
    Blueprint, jsonify, request, redirect, url_for,
    render_template, flash, current_app, send_from_directory
)
from werkzeug.utils import secure_filename

files_bp = Blueprint('files', __name__)

@files_bp.route('/files', methods=['GET', 'POST'])
def files():
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
                filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
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
                return redirect(url_for('files.files'))
        else:
            response = {'status': 'error', 'message': 'No valid files were uploaded.'}
            return jsonify(response), 400

    query = request.args.get('query', '').strip().lower()
    all_files = os.listdir(current_app.config['UPLOAD_FOLDER'])
    if query:
        filtered_files = [f for f in all_files if query in f.lower()]
    else:
        filtered_files = all_files
    return render_template('files.html', files=filtered_files, query=request.args.get('query', ''))

@files_bp.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    filename = secure_filename(filename)
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

@files_bp.route('/delete/<filename>', methods=['POST'])
def delete_file(filename):
    filename = secure_filename(filename)
    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
            flash(f'File "{filename}" has been deleted successfully.', 'success')
        except Exception as e:
            flash(f'Error deleting file "{filename}": {str(e)}', 'danger')
    else:
        flash(f'File "{filename}" does not exist.', 'warning')
    return redirect(url_for('files.files'))
