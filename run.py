import sys
import threading
import webview
from application import create_app
from application.utils import get_local_ip

FLASK_HOST = '0.0.0.0'
FLASK_PORT = 8080

def start_flask(app):
    app.run(host=FLASK_HOST, port=FLASK_PORT)

if __name__ == '__main__':
    app = create_app()

    flask_thread = threading.Thread(target=start_flask, args=(app,))
    flask_thread.daemon = True
    flask_thread.start()

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
