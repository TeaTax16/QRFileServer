# application/routes/webrtc.py

from flask import Blueprint, render_template

webrtc_bp = Blueprint('webrtc', __name__)

@webrtc_bp.route('/webrtc')
def webrtc():
    """
    Placeholder page for WebRTC.
    """
    return render_template('webrtc.html')
