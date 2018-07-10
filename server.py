import tornado.ioloop
import tornado.web
import tornado.websocket
import socket
from tornado.options import define, options, parse_command_line

from handlers import WSHandler

define("port", default=8888, help="run on the given port", type=int)

# we gonna store clients in dictionary..
clients = dict()

app = tornado.web.Application([
    (r'/ws', WSHandler),
])

if __name__ == '__main__':
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(8888)
    myIP = socket.gethostbyname(socket.gethostname())
    print('*** Websocket Server Started at %s***' % myIP)
    tornado.ioloop.IOLoop.instance().start()
