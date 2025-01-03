# run.py

import sys
import threading
import webview
from application import create_app
from application.utils import get_local_ip

FLASK_HOST = '0.0.0.0'
FLASK_PORT = 8080

def start_flask(app):
    app.run(host=FLASK_HOST, port=FLASK_PORT, threaded=True)

if __name__ == '__main__':
    app = create_app()

    # Start Flask app in a separate thread
    flask_thread = threading.Thread(target=start_flask, args=(app,))
    flask_thread.daemon = True
    flask_thread.start()

    # Get local IP address
    local_ip = get_local_ip()
    if not local_ip:
        print("Error: Could not determine local IP address.")
        sys.exit(1)
    else:
        window_title = "XARhub"
        window_url = f"http://{local_ip}:{FLASK_PORT}/"
        webview.create_window(
            window_title,
            window_url,
            confirm_close=True
        )
        webview.start()
