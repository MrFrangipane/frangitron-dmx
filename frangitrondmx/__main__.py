import os
import sys
from streamer import Streamer
from webapp import serve_webapp
from program_editor import launch_editor


if __name__ == '__main__':
    if len(sys.argv) == 2:
        if os.path.isfile(sys.argv[1]):
            programs_file = sys.argv[1]
            serve_webapp(Streamer(programs_file))

        elif sys.argv[1] == "editor":
            launch_editor()

    elif len(sys.argv) == 3 and sys.argv[1] == "editor" and os.path.isfile(sys.argv[2]):
        launch_editor(sys.argv[2])

    else:
        serve_webapp(Streamer())
