from gevent import monkey
from app import app, socketio

monkey.patch_all()

if __name__ == '__main__':
    socketio.run(app, host = "127.0.0.1", port = 5000, debug=True)
