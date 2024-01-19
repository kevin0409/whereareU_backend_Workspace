from app import create_app
from werkzeug.serving import make_ssl_devcert, run_simple
import os

app = create_app()

if __name__ == '__main__':
    cert_path = '/Users/parkseungho/Desktop/webserver/cert.pem'
    key_path = '/Users/parkseungho/Desktop/webserver/key.pem'

    if not (os.path.exists(cert_path) and os.path.exists(key_path)):
        make_ssl_devcert(cert_path, key_path, host='localhost', port=443)
    run_simple('localhost', 443, app, ssl_context=(cert_path, key_path), use_debugger=True)