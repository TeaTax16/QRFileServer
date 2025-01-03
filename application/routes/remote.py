# application/routes/remote.py

import os
import base64
import random
import string
import re
import hashlib
import requests
from flask import (
    Blueprint, render_template, request, flash, redirect, url_for, current_app
)
from werkzeug.utils import secure_filename
from application.utils import (
    generate_qr_code,
    create_pdf_with_qr,
    generate_qr_pdf_in_memory
)

remote_bp = Blueprint('remote', __name__)

# Simple regex to validate emails. Adjust as needed.
EMAIL_REGEX = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")

@remote_bp.route('/remote', methods=['GET', 'POST'])
def remote_room():
    if request.method == 'POST':
        # Get client names and emails
        client_names = request.form.getlist('client_names[]')
        client_emails = request.form.getlist('client_emails[]')

        # Clean up names (strip whitespace)
        clients = [
            (name.strip(), email.strip())
            for name, email in zip(client_names, client_emails)
            if name.strip()
        ]

        if not clients:
            flash('Please enter at least one client with a name.', 'warning')
            return redirect(url_for('remote.remote_room'))

        # Validate emails
        for _, email in clients:
            if not EMAIL_REGEX.match(email):
                flash(f'Invalid email format: {email}', 'warning')
                return redirect(url_for('remote.remote_room'))

        # Generate unique room code
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        current_app.remote_rooms[code] = {
            'host_url': None,
            'clients_url': []
        }

        # Generate host URL and QR code
        host_code = f"{code}/h"
        encoded_host = base64.urlsafe_b64encode(host_code.encode()).decode().rstrip('=')
        host_url = f"simxar://{encoded_host}"
        current_app.remote_rooms[code]['host_url'] = host_url
        host_qr = generate_qr_code(host_url)

        # Paths and logo
        codes_folder = current_app.config['CODES_FOLDER']
        logo_path = os.path.join(current_app.static_folder, 'media', 'simxar.png')

        # Save host QR code PDF to disk
        host_pdf_path = os.path.join(codes_folder, f"{code}_host_qr.pdf")
        create_pdf_with_qr(host_qr, host_pdf_path, "Host", logo_path=logo_path)

        client_qrs = []
        for client_name, client_email in clients:
            # Hash the email
            hashed_email = hashlib.sha256(client_email.lower().encode()).hexdigest()
            client_code = f"{code}/c/{client_name}/{hashed_email}"
            encoded_client = base64.urlsafe_b64encode(client_code.encode()).decode().rstrip('=')
            client_url = f"simxar://{encoded_client}"
            current_app.remote_rooms[code]['clients_url'].append(client_url)
            client_qr = generate_qr_code(client_url)
            client_qrs.append((client_name, client_email, client_qr))

        # Send each client their QR code via email using the email server
        for client_name, client_email, client_qr in client_qrs:
            client_pdf_buffer = generate_qr_pdf_in_memory(
                client_qr, "Client", client_name=client_name, logo_path=logo_path
            )

            # Prepare email payload
            email_payload = {
                "recipient": client_email,
                "subject": f"Remote Room Invitation - {code}",
                "body": (
                    f"Hello {client_name},\n\n"
                    f"You have been invited to join room \"{code}\".\n"
                    "Print the attached PDF, place it in the middle of your environment, and launch the simXAR app on your headset."
                ),
                "attachments": [
                    {
                        "filename": f"{code}_client_{client_name}_qr.pdf",
                        "content": base64.b64encode(client_pdf_buffer.getvalue()).decode('utf-8')
                    }
                ]
            }

            # Send email via the email server
            try:
                response = requests.post(
                    current_app.config['EMAIL_SERVER_URL'],
                    json=email_payload,
                    headers={
                        'Authorization': f'Bearer {current_app.config["EMAIL_SERVER_API_KEY"]}'
                    },
                    timeout=10  # seconds
                )
                response_data = response.json()
                if response.status_code != 200:
                    flash(
                        f"Failed to send email to {client_email}: {response_data.get('message', 'Unknown error')}",
                        'danger'
                    )
            except requests.exceptions.RequestException as e:
                flash(f"Error sending email to {client_email}: {str(e)}", 'danger')

        flash(
            f'Remote room "{code}" created successfully with {len(client_qrs)} client(s). '
            f'The host code PDF has been saved and the client QR codes have been emailed.',
            'success'
        )
        return render_template('remote_success.html', code=code)

    return render_template('remote.html')
