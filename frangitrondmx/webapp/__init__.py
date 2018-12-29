import os
from uuid import uuid4 as uuid
from subprocess import check_output, CalledProcessError
from flask import Flask, render_template, request, send_from_directory
from flask_socketio import SocketIO, emit


_app = Flask(__name__)
_app.config['SECRET_KEY'] = 'thefr4ngitronv8rysecretk$y'
_socketio = SocketIO(_app)
_namespace = '/frangitron-dmx'
_static_file_uuid = str(uuid())
_streamer = None


def _ip_address():
    cmd = "hostname -I"
    try:
        return check_output(cmd, shell=True).decode('utf-8').strip()
    except CalledProcessError:
        return "<unavailable>"


@_app.route('/js/<path:path>')
def _js(path):
    return send_from_directory('js', path)


@_app.route('/css/<path:path>')
def _css(path):
    return send_from_directory('css', path)


@_app.route('/')
def index():
    global _streamer

    if request.args.get('raspberrypi', False):
        column_count = 4
        footer = "<td><input id='reboot-gnome' type='submit' value='Reboot GNOME' class='raspi-only footer'></form></td>"
        footer += "<td><form method='POST' action='#'><input id='shutdown' type='submit' value='Shutdown' class='raspi-only footer'></form></td>"
        footer += "<td><form method='POST' action='#'><input id='restart-service' type='submit' value='Restart service' class='raspi-only footer'></form></td>"
    else:
        column_count = 2
        footer = "<td></td>"

    cell_template = \
        "<td class='{width}'>" \
            "<form method='POST' action='#'>" \
                "<input id='{program_name}' type='submit' value='{program_caption}' class='{class_}'>" \
            "</form>" \
        "</td>"

    row_count = len(_streamer.program_names) / column_count
    cells = list()

    for row in range(row_count + 1):
        cells.append(list())

        for col in range(column_count):
            program_index = row * column_count + col
            if program_index >= len(_streamer.programs): break

            cells[row].append(cell_template.format(
                program_name=_streamer.program_names[program_index],
                program_caption=_streamer.program_names[program_index].replace('_', ' '),
                class_='active' if _streamer.selected_program_id == program_index else '',
                width='four' if request.args.get('landscape', False) else 'two'
            ))

    if _streamer.programs:
        programs_table = "<table><tr>{rows}</tr></table>".format(
            rows='</tr>\n<tr>'.join(['\n'.join(row) for row in cells])
        )
    else:
        programs_table = "<i>No program loaded</i>"

    return render_template(
        'index.html',
        uuid=_static_file_uuid,
        programs_table=programs_table,
        ip_address=_ip_address(),
        footer=footer
    )


@_socketio.on('connection', namespace=_namespace)
def test_message(message):
    pass


@_socketio.on('program_clicked', namespace=_namespace)
def test_broadcast_message(message):
    global _streamer
    _streamer.program_clicked(message['program_name'])

    emit(
        'update_ui',
        {'ui_status': _streamer.ui_status()},
        broadcast=True
    )


@_socketio.on('ping', namespace=_namespace)
def ping_pong():
    emit('pong')


@_socketio.on('reboot-gnome', namespace=_namespace)
def reboot_gnome():
    if os.path.isfile('/home/pi/.config/lxsession/LXDE-pi/autostart.disabled'):
        os.rename(
            '/home/pi/.config/lxsession/LXDE-pi/autostart.disabled',
            '/home/pi/.config/lxsession/LXDE-pi/autostart'
        )
    else:
        os.rename(
            '/home/pi/.config/lxsession/LXDE-pi/autostart',
            '/home/pi/.config/lxsession/LXDE-pi/autostart.disabled',
        )
    os.system('reboot now')


@_socketio.on('restart-service', namespace=_namespace)
def restart_service():
    global _streamer
    _streamer.stop()
    os.system("systemctl restart frangitron-dmx")


@_socketio.on('shutdown', namespace=_namespace)
def shutdown():
    global _streamer
    _streamer.stop()
    os.system("shutdown now")


def update():
    os.system("/home/pi/dmxenv/bin/pip install git+http://github.com/mrfrangipane/frangitron-dmx.git")


def serve_webapp(streamer):
    global _streamer
    _streamer = streamer

    _socketio.run(
        _app,
        debug=True,
        use_reloader = False,
        host='0.0.0.0'
    )
