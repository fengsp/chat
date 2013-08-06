"""
The project start file...
"""
import os, sys
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from chat.views import app
from gevent import monkey
from socketio.server import SocketIOServer
import werkzeug.serving

monkey.patch_all()

reload(sys)
sys.setdefaultencoding('utf-8')

@werkzeug.serving.run_with_reloader
def run_socket_server():
    app.debug = True
    port = 8000
    SocketIOServer(('', port), app, resource="socket.io").serve_forever()


if __name__ == '__main__':
    run_socket_server()
