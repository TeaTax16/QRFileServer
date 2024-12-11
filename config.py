# config.py
import os
import sys  # Import sys to use in getattr

# Configuration Constants
SECRET_KEY = 'your_secret_key'  # Replace with a secure key in production
UPLOAD_FOLDER_NAME = 'uploads'
CODES_FOLDER_NAME = 'codes'
FLASK_HOST = '0.0.0.0'
FLASK_PORT = 8080

# Determine the base path based on execution context
if getattr(sys, 'frozen', False):
    # Running as a bundled executable
    APP_BASE_PATH = os.path.dirname(sys.executable)
else:
    # Running as a standard script
    APP_BASE_PATH = os.path.abspath("")

# Setup upload and codes folders
UPLOAD_FOLDER = os.path.join(APP_BASE_PATH, UPLOAD_FOLDER_NAME)
CODES_FOLDER = os.path.join(APP_BASE_PATH, CODES_FOLDER_NAME)

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(CODES_FOLDER, exist_ok=True)
