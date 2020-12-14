#
# Created by maks5507 (me@maksimeremeev.com)
#


import pika
import pika.spec
import traceback
import sys


def consumer_function(function):
    """
    :param function: Message processing function to wrap. Should take only body and properties parameters.
    """

    def process(channel, method, header, body):
        properties = header
        result = function(body, properties)
        channel.basic_ack(delivery_tag=method.delivery_tag)
        if result is not None:
            reply_to = properties.reply_to
            channel.basic_publish(exchange='', routing_key=reply_to, body=result)
    return process


def class_consumer(function):
    """
    :param function: Message processing clsass method to wrap. Should take only self, body and properties parameters.
    """

    def process(self, channel, method, header, body):
        properties = header
        result = function(self, body, properties)
        channel.basic_ack(delivery_tag=method.delivery_tag)
        if result is not None:
            reply_to = properties.reply_to
            channel.basic_publish(exchange='', routing_key=reply_to, body=result)
    return process


def noexcept(function):
    def process(*args, **kwargs):
        try:
            return_value = function(*args, **kwargs)
            return return_value
        except:
            print(traceback.format_exc(), file=sys.stderr)
            args[0].connect()

    return process


class RabbitMQInterface:

    def __init__(self, user=None, password=None, host='localhost', port=5672, url_parameters=None):
        """
        :param user: username for RabbitMQ
        :param password: password for RabbitMQ
        :param host: RabbitMQ host. Default - localhost.
        :param port: RabbitMQ port. Default - 5672.
        :param url_parameters: (Optional) RabbitMQ credentials in a single line. Example: 'amqp://guest:guest@localhost:5672'
        """
        if url_parameters is None and user is None:
            raise Exception('Either url parameters or user and password must be set')
        self.user = user
        self.password = password
        self.url_parameters = url_parameters
        self.host = host
        self.port = port
        self.connect()

    def connect(self):
        """
        Connects to RabbitMQ, using the credentials specified in init.
        """
        self.connection, self.channel = self.__connect(self.user, self.password, self.host, self.port,
                                                       self.url_parameters)

    @staticmethod
    def __connect(user, passw, host, port, url_parameters):
        if url_parameters is not None:
            parameters = pika.URLParameters(url_parameters)
        else:
            credentials = pika.PlainCredentials(user, passw)
            parameters = pika.ConnectionParameters(host, port, credentials=credentials, heartbeat=0)

        connection = pika.BlockingConnection(parameters)
        channel = connection.channel()
        return connection, channel

    @noexcept
    def create_queue(self, name=None, exchnage_to_bind=None, binding_routing_key=''):
        if name is not None:
            result = self.channel.queue_declare(name)
        else:
            result = self.channel.queue_declare('', auto_delete=True)
        queue_name = result.method.queue
        if exchnage_to_bind is not None:
            self.channel.queue_bind(exchange=exchnage_to_bind, queue=queue_name, routing_key=binding_routing_key)
        return queue_name

    @noexcept
    def publish(self, routing_key, body, exchange='amq.topic', reply_to=None):
        """
        Publishes message to queue without waiting for response.
        :param routing_key: Queue to publish name
        :param body: Message text
        :param exchange: (Optional) Exchange to publish message. Default - 'amq.topic'
        :param reply_to: (Optional) Queue to response name
        """
        properties = pika.spec.BasicProperties(reply_to=reply_to)
        self.channel.basic_publish(exchange=exchange, routing_key=routing_key, body=body, properties=properties)

    @noexcept
    def fetch(self, routing_key, body, exchange='amq.topic'):
        """
        Publishes message and waits for response. To convey the response creates anonymous queue.
        :param routing_key: Queue to publish name
        :param body: Message text
        :param exchange: (Optional) Exchange to publish message. Default - 'amq.topic'
        """
        reply_to = self.create_queue()
        self.publish(exchange=exchange, routing_key=routing_key, body=body, reply_to=reply_to)
        for method_frame, properties, body in self.channel.consume(reply_to):
            self.channel.cancel()
        return body

    @noexcept
    def listen(self, queue, func):
        """
        Listens for all messages in specified queue.
        :param queue: Queue to listen
        :param func: Function processing messages. Must be decorated with either @rmq_interface.consumer_function
        or @rmq.interface.class_consumer
        """
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(queue, func)
        self.channel.start_consuming()
