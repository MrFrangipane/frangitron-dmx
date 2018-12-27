import os
import sys
from streamer import Streamer
from webapp import serve_webapp
from program_editor import launch_editor


if __name__ == '__main__':
    if len(sys.argv) > 1:
        if os.path.isfile(sys.argv[1]):
            programs_file = sys.argv[1]
            serve_webapp(Streamer(programs_file))

        elif sys.argv[1] == "editor":
            launch_editor()

    else:
        serve_webapp(Streamer())
