# from tornado.websocket import WebSocketHandler
#
#
# class WSHandler(WebSocketHandler):
#
#     def check_origin(self, origin):
#         return True
#
#     def open(self):
#         print('new connection')
#         self.write_message("Hello World")
#
#     def on_message(self, message):
#         print('message received %s' % message)
#
#     def on_close(self):
#         print('connection closed')

import tornado
import pika
from tornado.websocket import WebSocketHandler

from rabbitmqConsumer import ExampleConsumer

# ioloop = tornado.ioloop.IOLoop.current()


class WSHandler(WebSocketHandler):

    def __init__(self, application, request, **kwargs):
        super().__init__(application, request, **kwargs)

        self.q_me = self.get_argument("q_me", "test_me", True)
        self.q_other = self.get_argument("q_other", "test_other", True)
        self.consumer = ExampleConsumer(self.q_me, self)

    def check_origin(self, origin):
        return True

    def open(self):
        print('new connection')
        self.consumer.run()

    def on_message(self, message):
        connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        channel = connection.channel()

        channel.queue_declare(queue=self.q_other)

        channel.basic_publish(exchange='',
                              routing_key=self.q_other,
                              body=message)
        print(" message sent")
        connection.close()

    def on_close(self):
        print('connection closed')
        self.consumer.stop()













