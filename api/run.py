from app import create_app
from werkzeug.serving import run_simple

app = create_app()

if __name__ == '__main__':
    
    run_simple('127.0.0.1', 5000, app, threaded=True)