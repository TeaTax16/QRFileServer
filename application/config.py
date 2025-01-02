# application/config.py

import os

SECRET_KEY = 'your_secret_key'  # Replace with a secure key in production
FLASK_PORT = 8080

# Email Server Configuration
EMAIL_SERVER_URL = os.getenv('EMAIL_SERVER_URL', 'http://localhost:5001/send-email')
EMAIL_SERVER_API_KEY = os.getenv('EMAIL_SERVER_API_KEY', 'your_secure_api_key')  # Replace with your actual API key
