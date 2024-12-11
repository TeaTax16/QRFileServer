# routes/remote.py
import os
import sys
import base64
import random
import string
import io
from flask import Blueprint, render_template, request, flash
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from PIL import Image
import qrcode

from config import CODES_FOLDER
from utils import resource_path

remote_bp = Blueprint('remote', __name__)

# In-memory storage for remote rooms
remote_rooms = {}

@remote_bp.route('/remote', methods=['GET', 'POST'])
def remote_room():
    """
    Create a new remote room with unique codes and QR codes.
    Handles both displaying the client input form and processing the submitted client names.
    """
    if request.method == 'POST':
        # Retrieve client names from the form
        client_names = request.form.getlist('client_names[]')
        # Clean client names: remove empty names and strip whitespace
        client_names = [name.strip() for name in client_names if name.strip()]

        if not client_names:
            flash('Please enter at least one client name.', 'warning')
            return redirect(url_for('remote.remote_room'))

        # Generate a random 6-character alphanumeric code
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

        # Initialize room information
        remote_rooms[code] = {
            'host_url': None,
            'clients_url': []
        }

        # Define role-specific codes
        host_code = f"{code}/h"

        # Encode host code using URL-safe Base64 without padding
        encoded_host = base64.urlsafe_b64encode(host_code.encode()).decode().rstrip('=')

        # Generate simxar URL for host
        host_url = f"simxar://{encoded_host}"

        # Update room information
        remote_rooms[code]['host_url'] = host_url

        # Generate QR code for host
        host_qr = qrcode.make(host_url)

        # Generate QR codes for each client
        client_qrs = []
        for client_name in client_names:
            client_code = f"{code}/c/{client_name}"
            encoded_client = base64.urlsafe_b64encode(client_code.encode()).decode().rstrip('=')
            client_url = f"simxar://{encoded_client}"
            remote_rooms[code]['clients_url'].append(client_url)
            client_qr = qrcode.make(client_url)
            client_qrs.append((client_name, client_qr))

        # Generate PDFs for host and clients
        host_pdf_path = os.path.join(CODES_FOLDER, f"{code}_host_qr.pdf")
        client_pdf_paths = []

        logo_path = resource_path(os.path.join('static', 'media', 'simxar.png'))

        def save_qr_as_pdf(qr_image, output_path, role_label, client_name=None):
            """Helper function to save QR code to a PDF with logo and role label."""
            pdf_canvas = canvas.Canvas(output_path, pagesize=A4)

            # Dimensions
            qr_size = 17 * cm
            x_qr, y_qr = (A4[0] - qr_size) / 2, ((A4[1] - qr_size) / 2) - 1 * cm

            # Draw the logo at the top
            logo_width = 10 * cm
            logo_height = 10 * cm
            x_logo = (A4[0] - logo_width) / 2
            y_logo = A4[1] - logo_height - 1 * cm
            pdf_canvas.drawImage(logo_path, x_logo, y_logo, logo_width, logo_height, preserveAspectRatio=True)

            # Save QR code as a temporary PNG and draw it
            qr_temp_path = "temp_qr.png"
            qr_image = qr_image.resize((int(qr_size), int(qr_size)))  # Ensure consistent size
            qr_image.save(qr_temp_path)
            pdf_canvas.drawImage(qr_temp_path, x_qr, y_qr, qr_size, qr_size)
            os.remove(qr_temp_path)  # Clean up temporary file

            # Add label below the QR code
            pdf_canvas.setFont("Helvetica-Bold", 24)
            if client_name:
                label = f"{role_label} - {client_name}"
            else:
                label = role_label
            text_x = A4[0] / 2
            text_y = y_qr - 2 * cm  # Position below the QR code
            pdf_canvas.drawCentredString(text_x, text_y, label)

            # Finalize the page
            pdf_canvas.showPage()
            pdf_canvas.save()

        # Generate host PDF
        save_qr_as_pdf(host_qr, host_pdf_path, "Host")

        # Generate client PDFs
        for client_name, client_qr in client_qrs:
            client_pdf_path = os.path.join(CODES_FOLDER, f"{code}_client_{client_name}_qr.pdf")
            save_qr_as_pdf(client_qr, client_pdf_path, "Client", client_name=client_name)
            client_pdf_paths.append(client_pdf_path)

        flash(f'Remote room "{code}" created successfully with {len(client_qrs)} client(s). QR codes have been generated and stored.', 'success')
        return render_template('remote_success.html', code=code)

    # For GET request, render the client input form
    return render_template('remote.html')
