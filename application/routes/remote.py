import os
import base64
import random
import string
import io
import re
import hashlib
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from PIL import Image
import qrcode
from flask import (
    Blueprint, render_template, request, flash, redirect, url_for, current_app
)
from werkzeug.utils import secure_filename
from flask_mail import Message
from reportlab.lib.utils import ImageReader

remote_bp = Blueprint('remote', __name__)

# Simple regex to validate emails. You can adjust this if needed.
EMAIL_REGEX = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")

@remote_bp.route('/remote', methods=['GET', 'POST'])
def remote_room():
    if request.method == 'POST':
        # Get client names and emails
        client_names = request.form.getlist('client_names[]')
        client_emails = request.form.getlist('client_emails[]')

        # Clean up names (strip whitespace)
        clients = [(name.strip(), email.strip()) for name, email in zip(client_names, client_emails) if name.strip()]

        if not clients:
            flash('Please enter at least one client with a name.', 'warning')
            return redirect(url_for('remote.remote_room'))

        # Validate emails
        for _, email in clients:
            if not EMAIL_REGEX.match(email):
                flash(f'Invalid email format: {email}', 'warning')
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

        # Save host QR code PDF to disk
        host_pdf_path = os.path.join(current_app.config['CODES_FOLDER'], f"{code}_host_qr.pdf")

        def save_qr_as_pdf(qr_image, output_path, role_label, client_name=None):
            pdf_canvas = canvas.Canvas(output_path, pagesize=A4)
            qr_size = 17 * cm
            x_qr, y_qr = (A4[0] - qr_size) / 2, ((A4[1] - qr_size) / 2) - 1 * cm

            logo_path = os.path.join(current_app.static_folder, 'media/simxar.png')
            if os.path.exists(logo_path):
                logo_width = 10 * cm
                logo_height = 10 * cm
                x_logo = (A4[0] - logo_width) / 2
                y_logo = A4[1] - logo_height - 1 * cm
                pdf_canvas.drawImage(logo_path, x_logo, y_logo, logo_width, logo_height, preserveAspectRatio=True)

            # Save QR code as PNG temporarily
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

        # Generate and save the host PDF
        save_qr_as_pdf(host_qr, host_pdf_path, "Host")

        client_qrs = []
        for client_name, client_email in clients:
            # Hash the email
            hashed_email = hashlib.sha256(client_email.lower().encode()).hexdigest()
            client_code = f"{code}/c/{client_name}/{hashed_email}"
            encoded_client = base64.urlsafe_b64encode(client_code.encode()).decode().rstrip('=')
            client_url = f"simxar://{encoded_client}"
            current_app.remote_rooms[code]['clients_url'].append(client_url)
            client_qr = qrcode.make(client_url)
            client_qrs.append((client_name, client_email, client_qr))

        # Generate client PDFs in memory and send via email
        def generate_qr_pdf_in_memory(qr_image, role_label, client_name=None):
            pdf_buffer = io.BytesIO()
            pdf_canvas = canvas.Canvas(pdf_buffer, pagesize=A4)

            qr_size = 17 * cm
            x_qr, y_qr = (A4[0] - qr_size) / 2, ((A4[1] - qr_size) / 2) - 1 * cm

            logo_path = os.path.join(current_app.static_folder, 'media/simxar.png')
            if os.path.exists(logo_path):
                logo_width = 10 * cm
                logo_height = 10 * cm
                x_logo = (A4[0] - logo_width) / 2
                y_logo = A4[1] - logo_height - 1 * cm
                pdf_canvas.drawImage(logo_path, x_logo, y_logo, logo_width, logo_height, preserveAspectRatio=True)

            # Convert QR image to PNG in memory
            qr_temp = io.BytesIO()
            qr_pil_image = qr_image.get_image().resize((int(qr_size), int(qr_size)))
            qr_pil_image.save(qr_temp, format='PNG')
            qr_temp.seek(0)

            # Use ImageReader for BytesIO
            image_reader = ImageReader(qr_temp)
            pdf_canvas.drawImage(image_reader, x_qr, y_qr, qr_size, qr_size)

            pdf_canvas.setFont("Helvetica-Bold", 24)
            label = f"{role_label}" if not client_name else f"{role_label} - {client_name}"
            text_x = A4[0] / 2
            text_y = y_qr - 2 * cm
            pdf_canvas.drawCentredString(text_x, text_y, label)

            pdf_canvas.showPage()
            pdf_canvas.save()
            pdf_buffer.seek(0)
            return pdf_buffer

        # Send each client their QR code via email
        for client_name, client_email, client_qr in client_qrs:
            client_pdf_buffer = generate_qr_pdf_in_memory(client_qr, "Client", client_name=client_name)

            msg = Message(subject=f"Your Remote Room QR Code - {code}",
                          recipients=[client_email])
            msg.body = (
                f"Hello {client_name},\n\n"
                f"Attached is the QR code to join the remote room \"{code}\".\n"
                "Simply scan it with the XARhub application.\n\n"
                "Best,\n"
                "XARhub Team"
            )

            # Attach the client's PDF
            msg.attach(f"{code}_client_{client_name}_qr.pdf", "application/pdf", client_pdf_buffer.getvalue())
            current_app.mail.send(msg)

        flash(f'Remote room "{code}" created successfully with {len(client_qrs)} client(s). '
              f'The host code PDF has been saved and the client QR codes have been emailed.', 'success')
        return render_template('remote_success.html', code=code)

    return render_template('remote.html')
