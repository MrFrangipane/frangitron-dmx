from streamer import Streamer
from webapp import serve_webapp


if __name__ == '__main__':
    serve_webapp(Streamer())
