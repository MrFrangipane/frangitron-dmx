# Frangitron DMX

Small python web DMX Controller for Raspberry Pi 3

## Autostart

Edit file

````bash
$ sudo nano /home/pi/.config/lxsession/LXDE-pi/autostart
````

To be :

````bash
@xset s noblank
@xset s off
@xset –dpms
@chromium-browser --kiosk --app=http://localhost:5000/?raspberrypi=true
````

## Programs

Are based on `eval` where `elapsed` is time in seconds and `math` is the `math` module

````json
{
    'Blackout': {},
    'GreenYellow' : {
        1: "0.5 * math.cos(elapsed * math.pi * 0.25) + 0.5",
        2: "0.5 * math.cos(elapsed * math.pi * 0.25 + math.pi) + 0.5"
    },
    'Strobe': {
        1: "1.0 if elapsed % .1 > 0.05 else 0.0",
        2: "1.0 if elapsed % .1 > 0.05 else 0.0",
        3: "1.0 if elapsed % .1 > 0.05 else 0.0"
    }
}
````
