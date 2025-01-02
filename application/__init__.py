# application/__init__.py

import os
import sys

from flask import Flask

from .config import SECRET_KEY, FLASK_PORT, EMAIL_SERVER_URL, EMAIL_SERVER_API_KEY
from .utils import resource_path


def create_app():
    if getattr(sys, 'frozen', False):
        # Running as a bundled executable
        app_base_path = os.path.dirname(sys.executable)
    else:
        # Running as a standard script
        app_base_path = os.path.abspath("")

    UPLOAD_FOLDER_NAME = 'uploads'
    CODES_FOLDER_NAME = 'codes'

    UPLOAD_FOLDER = os.path.join(app_base_path, UPLOAD_FOLDER_NAME)
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    CODES_FOLDER = os.path.join(app_base_path, CODES_FOLDER_NAME)
    os.makedirs(CODES_FOLDER, exist_ok=True)

    app = Flask(
        __name__,
        template_folder=resource_path('templates'),
        static_folder=resource_path('static')
    )
    app.config['SECRET_KEY'] = SECRET_KEY
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    app.config['CODES_FOLDER'] = CODES_FOLDER
    app.config['FLASK_PORT'] = FLASK_PORT

    # Email Server Configuration
    app.config['EMAIL_SERVER_URL'] = EMAIL_SERVER_URL
    app.config['EMAIL_SERVER_API_KEY'] = EMAIL_SERVER_API_KEY

    # In-memory storage for remote rooms
    app.remote_rooms = {}

    # Import and register blueprints
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
