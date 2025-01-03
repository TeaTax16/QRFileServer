# application/utils.py

import os
import sys
import socket
import base64
import io
from PIL import Image
import qrcode
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.utils import ImageReader

def resource_path(relative_path):
    """
    Get absolute path to resource, works for dev and for PyInstaller.
    """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath("")
    return os.path.join(base_path, relative_path)

def get_local_ip():
    """
    Retrieve the local network IP address.
    """
    hostname = socket.gethostname()
    try:
        return socket.gethostbyname(hostname)
    except socket.gaierror:
        return None

def generate_qr_code(data):
    """
    Generate a QR code image from the provided data.
    """
    return qrcode.make(data)

def create_pdf_with_qr(qr_image, output_path, role_label, client_name=None, logo_path=None):
    """
    Create a PDF containing the QR code, optional logo, and label.
    """
    pdf_canvas = canvas.Canvas(output_path, pagesize=A4)
    qr_size = 17 * cm
    x_qr, y_qr = (A4[0] - qr_size) / 2, ((A4[1] - qr_size) / 2) - 1 * cm

    # Add logo if provided
    if logo_path and os.path.exists(logo_path):
        logo_width = 10 * cm
        logo_height = 10 * cm
        x_logo = (A4[0] - logo_width) / 2
        y_logo = A4[1] - logo_height - 1 * cm
        pdf_canvas.drawImage(logo_path, x_logo, y_logo, logo_width, logo_height, preserveAspectRatio=True)

    # Save QR code as PNG in memory
    qr_buffer = io.BytesIO()
    qr_pil_image = qr_image.resize((int(qr_size), int(qr_size)))
    qr_pil_image.save(qr_buffer, format='PNG')
    qr_buffer.seek(0)

    # Use ImageReader for BytesIO
    image_reader = ImageReader(qr_buffer)
    pdf_canvas.drawImage(image_reader, x_qr, y_qr, qr_size, qr_size)

    # Add label
    pdf_canvas.setFont("Helvetica-Bold", 24)
    label = f"{role_label}" if not client_name else f"{role_label} - {client_name}"
    text_x = A4[0] / 2
    text_y = y_qr - 2 * cm
    pdf_canvas.drawCentredString(text_x, text_y, label)

    pdf_canvas.showPage()
    pdf_canvas.save()

def generate_qr_pdf_in_memory(qr_image, role_label, client_name=None, logo_path=None):
    """
    Generate a PDF with QR code in memory and return as BytesIO.
    """
    pdf_buffer = io.BytesIO()
    pdf_canvas = canvas.Canvas(pdf_buffer, pagesize=A4)

    qr_size = 17 * cm
    x_qr, y_qr = (A4[0] - qr_size) / 2, ((A4[1] - qr_size) / 2) - 1 * cm

    # Add logo if provided
    if logo_path and os.path.exists(logo_path):
        logo_width = 10 * cm
        logo_height = 10 * cm
        x_logo = (A4[0] - logo_width) / 2
        y_logo = A4[1] - logo_height - 1 * cm
        pdf_canvas.drawImage(logo_path, x_logo, y_logo, logo_width, logo_height, preserveAspectRatio=True)

    # Convert QR image to PNG in memory
    qr_temp = io.BytesIO()
    qr_pil_image = qr_image.resize((int(qr_size), int(qr_size)))
    qr_pil_image.save(qr_temp, format='PNG')
    qr_temp.seek(0)

    # Use ImageReader for BytesIO
    image_reader = ImageReader(qr_temp)
    pdf_canvas.drawImage(image_reader, x_qr, y_qr, qr_size, qr_size)

    # Add label
    pdf_canvas.setFont("Helvetica-Bold", 24)
    label = f"{role_label}" if not client_name else f"{role_label} - {client_name}"
    text_x = A4[0] / 2
    text_y = y_qr - 2 * cm
    pdf_canvas.drawCentredString(text_x, text_y, label)

    pdf_canvas.showPage()
    pdf_canvas.save()
    pdf_buffer.seek(0)
    return pdf_buffer
