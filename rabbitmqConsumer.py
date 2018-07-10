import logging
import pika

LOG_FORMAT = ('%(levelname) -10s %(asctime)s %(name) -30s %(funcName) '
              '-35s %(lineno) -5d: %(message)s')
LOGGER = logging.getLogger(__name__)


class ExampleConsumer(object):
    # EXCHANGE = 'message'
    # EXCHANGE_TYPE = 'topic'
    # QUEUE = 'test'
    # ROUTING_KEY = 'example.text'

    def __init__(self, q_name, ws):

        #self.ioloop = ioloop
        self.websocket = ws
        self._connection = None
        self._channel = None
        self._closing = False
        self._consumer_tag = None
        self._queue = q_name
        # self._url = amqp_url

    def connect(self):

        print('Connecting..')
        return pika.TornadoConnection(pika.ConnectionParameters('localhost'),
                                      self.on_connection_open,
                                      stop_ioloop_on_close=False)

    def on_connection_open(self, unused_connection):

        print('Connection opened')
        self.add_on_connection_close_callback()
        self.open_channel()

    def add_on_connection_close_callback(self):

        print('Adding connection close callback')
        self._connection.add_on_close_callback(self.on_connection_closed)

    def on_connection_closed(self, connection, reply_code, reply_text):

        self._channel = None
        if self._closing:
            pass
            # self._connection.ioloop.stop()
            # self.ioloop.stop()
        else:
            print('Connection closed, reopening in 5 seconds: (%s) %s',
                           reply_code, reply_text)
            self._connection.add_timeout(5, self.reconnect)

    def reconnect(self):

        # This is the old connection IOLoop instance, stop its ioloop
        # self._connection.ioloop.stop()
        # self.ioloop.stop()

        if not self._closing:
            # Create a new connection
            self._connection = self.connect()

            # There is now a new connection, needs a new ioloop to run
            # self._connection.ioloop.start()
            # self.ioloop.start()

    def open_channel(self):

        print('Creating a new channel')
        self._connection.channel(on_open_callback=self.on_channel_open)

    def on_channel_open(self, channel):

        print('Channel opened')
        self._channel = channel
        self.add_on_channel_close_callback()
        # self.setup_exchange(self.EXCHANGE)
        self.setup_queue(self._queue)

    def add_on_channel_close_callback(self):

        print('Adding channel close callback')
        self._channel.add_on_close_callback(self.on_channel_closed)

    def on_channel_closed(self, channel, reply_code, reply_text):

        print('Channel %i was closed: (%s) %s',
                       channel, reply_code, reply_text)
        self._connection.close()

    # def setup_exchange(self, exchange_name):
    #
    #     LOGGER.info('Declaring exchange %s', exchange_name)
    #     self._channel.exchange_declare(self.on_exchange_declareok,
    #                                    exchange_name,
    #                                    self.EXCHANGE_TYPE)

    # def on_exchange_declareok(self, unused_frame):
    #
    #     LOGGER.info('Exchange declared')
    #     self.setup_queue(self.QUEUE)

    def setup_queue(self, queue_name):

        print('Declaring queue %s', queue_name)
        self._channel.queue_declare(self.on_queue_declareok, queue_name)

    def on_queue_declareok(self, method_frame):

        # LOGGER.info('Binding %s to %s with %s',
        #             self.EXCHANGE, self.QUEUE, self.ROUTING_KEY)
        # self._channel.queue_bind(self.on_bindok, self.QUEUE,
        #                          self.EXCHANGE, self.ROUTING_KEY)
        print('start consuming')
        self.start_consuming()

    # def on_bindok(self, unused_frame):
    #
    #     LOGGER.info('Queue bound')
    #     self.start_consuming()

    def start_consuming(self):

        print('Issuing consumer related RPC commands')
        self.add_on_cancel_callback()
        self._consumer_tag = self._channel.basic_consume(self.on_message,
                                                         self._queue)

    def add_on_cancel_callback(self):

        print('Adding consumer cancellation callback')
        self._channel.add_on_cancel_callback(self.on_consumer_cancelled)

    def on_consumer_cancelled(self, method_frame):

        print('Consumer was cancelled remotely, shutting down: %r',
                    method_frame)
        if self._channel:
            self._channel.close()

    def on_message(self, unused_channel, basic_deliver, properties, body):

        print('Received message # %s from %s: %s',
                    basic_deliver.delivery_tag, properties.app_id, body)
        self.acknowledge_message(basic_deliver.delivery_tag)
        self.websocket.write_message(body)

    def acknowledge_message(self, delivery_tag):

        print('Acknowledging message %s', delivery_tag)
        self._channel.basic_ack(delivery_tag)

    def stop_consuming(self):

        if self._channel:
            print('Sending a Basic.Cancel RPC command to RabbitMQ')
            self._channel.basic_cancel(self.on_cancelok, self._consumer_tag)

    def on_cancelok(self, unused_frame):

        print('RabbitMQ acknowledged the cancellation of the consumer')
        self.close_channel()

    def close_channel(self):

        print('Closing the channel')
        self._channel.close()

    def run(self):

        print("runing")
        self._connection = self.connect()
        # self._connection.ioloop.start()
        # self.ioloop.start()

    def stop(self):

        print('Stopping')
        self._closing = True
        self.stop_consuming()
        # self._connection.ioloop.start()
        print('Stopped')

    def close_connection(self):

        print('Closing connection')
        self._connection.close()
