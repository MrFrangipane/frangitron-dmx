import os
import sys
from streamer import Streamer
from webapp import serve_webapp


if __name__ == '__main__':
    programs_file = None
    if len(sys.argv) > 1 and os.path.isfile(sys.argv[1]):
        programs_file = sys.argv[1]

    serve_webapp(Streamer(programs_file))
