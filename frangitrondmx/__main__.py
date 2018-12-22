#!/usr/bin/env python
from uuid import uuid4 as uuid
from subprocess import check_output, CalledProcessError
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
static_file_uuid = str(uuid())
status = dict()

def _ip_address():
    cmd = "hostname -I"
    try:
        return check_output(cmd, shell=True).decode('utf-8')
    except CalledProcessError:
        return "[ip unavailable]"


@app.route('/js/<path:path>')
def _js(path):
    return send_from_directory('js', path)


@app.route('/css/<path:path>')
def _css(path):
    return send_from_directory('css', path)


@app.route('/')
def index():
    global status
    if not status.get('programs', False):
        status['programs'] = ['Get-out', 'Chatty', 'Lounge', 'Club', 'Apocalypse', 'Searchlight']
        status['selected_program'] = -1

    if request.args.get('landscape', False):
        column_count = 4
    else:
        column_count = 2

    cell_template = \
        "<td class='{width}'>" \
        "<form method='POST' action='#'><input id='{program_name}' type='submit' value='{program_name}' class='{class_}'></form>" \
        "</td>"

    row_count = len(status['programs']) / column_count
    cells = list()

    for row in range(row_count + 1):
        cells.append(list())

        for col in range(column_count):
            program_index = row * column_count + col
            if program_index >= len(status['programs']): continue

            cells[row].append(cell_template.format(
                program_name=status['programs'][program_index],
                class_='active' if status['selected_program'] == program_index else '',
                width='two' if request.args.get('landscape', False) else 'four'
            ))

    programs_table = "<table><tr>{rows}</tr></table>".format(
        rows='</tr>\n<tr>'.join(['\n'.join(row) for row in cells])
    )

    return render_template(
        'index.html',
        async_mode=socketio.async_mode,
        uuid=static_file_uuid,
        programs_table=programs_table,
        ip_address=_ip_address()
    )


@socketio.on('connection', namespace=namespace)
def test_message(message):
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit(
        'my_response',
        {
            'data': message['data'],
            'count': session['receive_count'],
            'type': 'connection'
        }
    )


@socketio.on('broadcast', namespace=namespace)
def test_broadcast_message(message):
    global status
    session['receive_count'] = session.get('receive_count', 0) + 1
    status['selected_program'] = status['programs'].index(message['data'])
    emit(
        'my_response',
        {
            'data': message['data'],
            'count': session['receive_count'],
            'type': 'broadcast'
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
    socketio.run(app, debug=True, host='0.0.0.0')
