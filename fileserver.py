from flask import Flask, send_from_directory, jsonify, request, redirect, url_for, render_template_string
import os
from werkzeug.utils import secure_filename

# Create a Flask app for file server management
app = Flask(__name__)

# Paths to the input and output folders
input_folder = r'directory/to/input/folder'
output_folder = r'directory/to/output/folder'

# Ensure the input and output folders exist
os.makedirs(input_folder, exist_ok=True)
os.makedirs(output_folder, exist_ok=True)

# Allowed file extensions
ALLOWED_EXTENSIONS = {'nrrd', 'nii', 'nii.gz', 'dcm', 'dicom'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# App URL to upload files to the server
# http://localhost:8080/upload
@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # Check if the POST request has the file part
        if 'file[]' not in request.files:
            return 'No file part in the request', 400
        # Retrieve list of files
        files = request.files.getlist('file[]')
        # Validate the files
        if not files or files[0].filename == '':
            return 'No selected files', 400
        
        # loop through each file to validate and save and add to array
        uploaded_filenames = []
        for file in files:
            if file.filename == '':
                continue  # Skip empty filenames
            if file and allowed_file(file.filename):
                # Securely save the file to the input folder
                filename = secure_filename(file.filename)
                file.save(os.path.join(input_folder, filename))
                uploaded_filenames.append(filename)
            else:
                return f'File type not allowed: {file.filename}', 400

        if uploaded_filenames:
            return redirect(url_for('upload_file', success=True))
        else:
            return 'No valid files uploaded', 400
    else:
        # Render the upload form
        success = request.args.get('success')
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
            ''', success=success)

# App URL to list all files in the server as a JSON
# http://localhost:8080/files
@app.route('/files', methods=['GET'])
def list_files():
    files = os.listdir(output_folder)
    return jsonify(files)

# App URL to download a specific file from the server
# http://localhost:8080/download/<filename>
@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    return send_from_directory(output_folder, filename, as_attachment=True)

# Initiate the localhost server
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)