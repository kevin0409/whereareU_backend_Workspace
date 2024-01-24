from app import create_app
from werkzeug.serving import run_simple
import os

app = create_app()

if __name__ == '__main__':

    app.run(host='127.0.0.1', port=5000, debug=True)