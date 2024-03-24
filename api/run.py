from app import create_app
from werkzeug.serving import run_simple



if __name__ == '__main__':
    app = create_app()
    run_simple('127.0.0.1', 5000, app, threaded = True)
    #app.run(debug=True)