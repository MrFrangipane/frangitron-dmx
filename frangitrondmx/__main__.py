#!/usr/bin/env python
from uuid import uuid4 as uuid
from flask import Flask, render_template, session, request, send_from_directory
from flask_socketio import SocketIO, emit, disconnect

# Set this variable to "threading", "eventlet" or "gevent" to test the
# different async modes, or leave it set to None for the application to choose
# the best option gased on installed packages.
async_mode = None

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode=async_mode)
namespace = '/frangitron-dmx'
js_file_uuid = str(uuid())


@app.route('/js/<path:path>')
def _js(path):
    return send_from_directory('js', path)


@app.route('/')
def index():
    return render_template(
        'index.html',
        async_mode=socketio.async_mode,
        uuid=js_file_uuid
    )


@socketio.on('connection', namespace=namespace)
def test_message(message):
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit(
        'my_response',
        {
            'data': message['data'],
            'count': session['receive_count']
        }
    )


@socketio.on('broadcast', namespace=namespace)
def test_broadcast_message(message):
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit(
        'my_response',
        {
            'data': message['data'],
            'count': session['receive_count']
        },
        broadcast=True
    )


@socketio.on('disconnect_request', namespace=namespace)
def disconnect_request():
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit(
        'my_response',
        {
            'data': 'Disconnected!',
            'count': session['receive_count']
        }
    )
    disconnect()


@socketio.on('ping', namespace=namespace)
def ping_pong():
    emit('pong')


@socketio.on('connect', namespace=namespace)
def test_connect():
    emit(
        'my_response',
        {
            'data': 'Connected',
            'count': 0
        }
    )


@socketio.on('disconnect', namespace=namespace)
def test_disconnect():
    print('Client disconnected', request.sid)


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0')
