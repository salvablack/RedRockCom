from flask import Flask, render_template
from flask_socketio import SocketIO, emit, join_room

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

@app.route('/')
def index():
    return render_template('index.html')

# Signaling WebRTC
@socketio.on('join')
def on_join(data):
    room = data['room']
    join_room(room)
    emit('status', {'msg': f'Unido a sala {room}'}, to=request.sid)
    emit('peer_joined', {'from': request.sid}, to=room, include_self=False)

@socketio.on('offer')
def on_offer(data):
    emit('offer', data, to=data['to'], include_self=False)

@socketio.on('answer')
def on_answer(data):
    emit('answer', data, to=data['to'], include_self=False)

@socketio.on('ice-candidate')
def on_ice(data):
    emit('ice-candidate', data, to=data['to'], include_self=False)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=False)
