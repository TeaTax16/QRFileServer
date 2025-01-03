# application/routes/qr.py

import os
import base64
import io
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from application.utils import generate_qr_code, get_local_ip

qr_bp = Blueprint('qr', __name__)

@qr_bp.route('/qr', methods=['GET'])
def qr_code():
    filename = request.args.get('filename')
    if not filename:
        return "Error: No filename provided.", 400

    filename = secure_filename(filename)
    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    if not os.path.exists(file_path):
        return "Error: File does not exist.", 404

    local_ip = get_local_ip()
    if not local_ip:
        return "Error: Could not determine local IP address.", 500

    download_url = f"http://{local_ip}:{current_app.config['FLASK_PORT']}/download/{filename}"
    img = generate_qr_code(download_url)
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    return jsonify({'qr_code': img_base64})
