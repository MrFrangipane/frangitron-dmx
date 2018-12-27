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

**A program is a set of channels associated to expressions.**

Channels and values are based on evil `eval` where `elapsed` is time in seconds and those modules are available

- `math`
- `random`

Each frame, values are computed according to selected program and expressions.

Universe expressions are not reset each program change, which means that for blackout you need to assign `"0"` to all relevant channels

This allows to fire specific fixtures without affecting other fixtures (see Smoke on / off in example)

Expressions are computed in `float` from 0.0 to 1.0, except if the expression starts with `$`. Then, expression ranges from `int` 0 to 255

This allows to express precise values for specific fixture programs (see Absolute values in example)

**Spaces are not allowed in program names** but _underscores are replaced with spaces in UI captions_

````json
{
    "Blackout": {
        "range(1, 256)": "0"
    },
    "Color_rotation" : {
        "1": "0.5 * math.cos(elapsed * math.pi * 0.25) + 0.5",
        "2": "0.5 * math.cos(elapsed * math.pi * 0.25 + math.pi) + 0.5",
        "3": "1.0 if elapsed % 1 > 0.5 else 0.0"
    },
    "Strobe": {
        "range(1, 4)": "1.0 if elapsed % .1 > 0.05 else 0.0"
    },
    "Smoke_on": {
        "16": "1"
    },
    "Smoke_off": {
        "16": "0"
    },
    "Absolute_values" : {
        "1": "$128",
        "2": "$0",
        "3": "$255"
  }
}
````
