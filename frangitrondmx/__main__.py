import os
from streamer import Streamer
from webapp import serve_webapp


if __name__ == '__main__':
    if os.path.isfile('/home/pi/.config/lxsession/LXDE-pi/autostart.disabled'):
        os.rename(
            '/home/pi/.config/lxsession/LXDE-pi/autostart.disabled',
            '/home/pi/.config/lxsession/LXDE-pi/autostart'
        )

    serve_webapp(Streamer())
