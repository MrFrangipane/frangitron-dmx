import os
import sys
from streamer import Streamer
from webapp import serve_webapp
from editor import launch_editor


if __name__ == '__main__':
    if len(sys.argv) == 3:
        if os.path.isdir(sys.argv[1]) and os.path.isfile(sys.argv[2]):
            fixtures_folder = sys.argv[1]
            programs_file = sys.argv[2]
            serve_webapp(Streamer(fixtures_folder, programs_file))

        if sys.argv[1] == "editor" and os.path.isdir(sys.argv[2]):
            fixtures_folder = sys.argv[2]
            launch_editor(fixtures_folder)
