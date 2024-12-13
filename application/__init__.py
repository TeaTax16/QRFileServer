import os
import sys
from flask import Flask
from .config import SECRET_KEY, FLASK_PORT
from .mail_config import (
    MAIL_SERVER, MAIL_PORT, MAIL_USE_TLS, MAIL_USERNAME, MAIL_PASSWORD, MAIL_DEFAULT_SENDER
)
from .utils import resource_path
from flask_mail import Mail

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

    app.config['MAIL_SERVER'] = MAIL_SERVER
    app.config['MAIL_PORT'] = MAIL_PORT
    app.config['MAIL_USE_TLS'] = MAIL_USE_TLS
    app.config['MAIL_USERNAME'] = MAIL_USERNAME
    app.config['MAIL_PASSWORD'] = MAIL_PASSWORD
    app.config['MAIL_DEFAULT_SENDER'] = MAIL_DEFAULT_SENDER

    mail = Mail(app)

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

    # Attach mail object to app so we can use it in views
    app.mail = mail

    return app
