from flask_socketio import SocketIO

class LocationModule:
    def __init__(self, socketio):
        self.socketio = socketio
        self.register_socketio_events()

    def register_socketio_events(self):
        @self.socketio.on('location_update')
        def handle_location_update(data):
            self.socketio.emit('location_updated', data)
