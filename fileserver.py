from flask import Flask, send_from_directory, jsonify
import os

# Create a Flask app for file server management
app = Flask(__name__)

# Change this
output_folder = r'directory/to/output/folder'

# App URL to list all files in the server as a JSON
# localhost:8080/files
@app.route('/files', methods = ['GET'])
def list_files():
    files = os.listdir(output_folder)
    return jsonify(files)

# App URL to download a specific file from the server
# localhost:8080/download/<filename>
@app.route('/download/<filename>', methods = ['GET'])
def download_file(filename):
    return send_from_directory(output_folder, filename, as_attachment=True)

# Initiate the localhost server
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)