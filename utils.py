# utils.py
import os
import sys  # Import sys as it's used in resource_path and get_local_ip
import base64
import socket
from werkzeug.utils import secure_filename

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
