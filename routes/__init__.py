# routes/__init__.py
from .home import home_bp
from .files import files_bp
from .remote import remote_bp
from .webrtc import webrtc_bp
from .segmentation import segmentation_bp

def register_routes(app):
    app.register_blueprint(home_bp)
    app.register_blueprint(files_bp)
    app.register_blueprint(remote_bp)
    app.register_blueprint(webrtc_bp)
    app.register_blueprint(segmentation_bp)
