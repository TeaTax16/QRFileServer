import os
import base64
import random
import string
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from PIL import Image
import qrcode
from flask import (
    Blueprint, render_template, request, flash, redirect, url_for, current_app
)
from werkzeug.utils import secure_filename

remote_bp = Blueprint('remote', __name__)

@remote_bp.route('/remote', methods=['GET', 'POST'])
def remote_room():
    if request.method == 'POST':
        client_names = request.form.getlist('client_names[]')
        client_names = [name.strip() for name in client_names if name.strip()]

        if not client_names:
            flash('Please enter at least one client name.', 'warning')
            return redirect(url_for('remote.remote_room'))

        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        current_app.remote_rooms[code] = {
            'host_url': None,
            'clients_url': []
        }

        host_code = f"{code}/h"
        encoded_host = base64.urlsafe_b64encode(host_code.encode()).decode().rstrip('=')
        host_url = f"simxar://{encoded_host}"

        current_app.remote_rooms[code]['host_url'] = host_url
        host_qr = qrcode.make(host_url)

        client_qrs = []
        for client_name in client_names:
            client_code = f"{code}/c/{client_name}"
            encoded_client = base64.urlsafe_b64encode(client_code.encode()).decode().rstrip('=')
            client_url = f"simxar://{encoded_client}"
            current_app.remote_rooms[code]['clients_url'].append(client_url)
            client_qr = qrcode.make(client_url)
            client_qrs.append((client_name, client_qr))

        host_pdf_path = os.path.join(current_app.config['CODES_FOLDER'], f"{code}_host_qr.pdf")
        client_pdf_paths = []
        logo_path = os.path.join(current_app.static_folder, 'media/simxar.png')

        def save_qr_as_pdf(qr_image, output_path, role_label, client_name=None):
            pdf_canvas = canvas.Canvas(output_path, pagesize=A4)
            qr_size = 17 * cm
            x_qr, y_qr = (A4[0] - qr_size) / 2, ((A4[1] - qr_size) / 2) - 1 * cm

            # Draw logo
            logo_width = 10 * cm
            logo_height = 10 * cm
            x_logo = (A4[0] - logo_width) / 2
            y_logo = A4[1] - logo_height - 1 * cm
            pdf_canvas.drawImage(logo_path, x_logo, y_logo, logo_width, logo_height, preserveAspectRatio=True)

            # Save QR code as PNG
            qr_temp_path = "temp_qr.png"
            qr_pil_image = qr_image.get_image().resize((int(qr_size), int(qr_size)))
            qr_pil_image.save(qr_temp_path)
            pdf_canvas.drawImage(qr_temp_path, x_qr, y_qr, qr_size, qr_size)
            os.remove(qr_temp_path)

            # Add label
            pdf_canvas.setFont("Helvetica-Bold", 24)
            label = f"{role_label}" if not client_name else f"{role_label} - {client_name}"
            text_x = A4[0] / 2
            text_y = y_qr - 2 * cm
            pdf_canvas.drawCentredString(text_x, text_y, label)

            pdf_canvas.showPage()
            pdf_canvas.save()

        # Generate host PDF
        save_qr_as_pdf(host_qr, host_pdf_path, "Host")

        # Generate client PDFs
        for client_name, client_qr in client_qrs:
            client_pdf_path = os.path.join(current_app.config['CODES_FOLDER'], f"{code}_client_{client_name}_qr.pdf")
            save_qr_as_pdf(client_qr, client_pdf_path, "Client", client_name=client_name)
            client_pdf_paths.append(client_pdf_path)

        flash(f'Remote room "{code}" created successfully with {len(client_qrs)} client(s). QR codes have been generated and stored.', 'success')
        return render_template('remote_success.html', code=code)

    return render_template('remote.html')

@remote_bp.route('/codes/<filename>', methods=['GET'])
def get_code_file(filename):
    filename = secure_filename(filename)
    return current_app.send_static_file(os.path.join(current_app.config['CODES_FOLDER'], filename))
