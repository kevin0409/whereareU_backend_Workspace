from flask import Flask, render_template
from flask_socketio import SocketIO
from .location_module import LocationModule

app = Flask(__name__)
socketio = SocketIO(app)
location_module = LocationModule(socketio)

@app.route('/')
def index():
    return render_template('index.html')
