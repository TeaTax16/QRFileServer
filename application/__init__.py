# application/__init__.py

import os
import sys
from flask import Flask
from .config import Config
from .utils import resource_path

def create_app():
    if getattr(sys, 'frozen', False):
        # Running as a bundled executable
        app_base_path = os.path.dirname(sys.executable)
    else:
        # Running as a standard script
        app_base_path = os.path.abspath("")

    # Define directories
    UPLOAD_FOLDER = os.path.join(app_base_path, Config.UPLOAD_FOLDER_NAME)
    CODES_FOLDER = os.path.join(app_base_path, Config.CODES_FOLDER_NAME)

    # Create directories if they don't exist
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(CODES_FOLDER, exist_ok=True)

    # Initialize Flask app
    app = Flask(
        __name__,
        template_folder=resource_path('templates'),
        static_folder=resource_path('static')
    )

    # Configure app
    app.config.from_object(Config)
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    app.config['CODES_FOLDER'] = CODES_FOLDER

    # In-memory storage for remote rooms
    app.remote_rooms = {}

    # Register Blueprints
    from .routes.main import main_bp
    from .routes.files import files_bp
    from .routes.webrtc import webrtc_bp
    from .routes.segmentation import segmentation_bp
    from .routes.remote import remote_bp
    from .routes.qr import qr_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(files_bp)
    app.register_blueprint(webrtc_bp)
    app.register_blueprint(segmentation_bp)
    app.register_blueprint(remote_bp)
    app.register_blueprint(qr_bp)

    return app
