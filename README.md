# RabbitMQ Interface

The high-level wrapper to the `pika` library, making interaction with `RabbitMQ` easy and efficient. The library presents a Publish-Fetch-Listen interface, which is a common standard for message queue-based software applications. 

**Author and Developer:**

- Maksim Eremeev (me@maksimeremeev.com)

## Requirements

- ```python>=3.6```
- ```pika>=1.0.1```


## Installation

```
sudo python setup.py build
sudo python setup.py install
```

## Connecting to RabbitMQ

Connection to RabbitMQ is established when creating `RabbitMQInteface` object. It requires a username, password, host, and port for instantiation. You can also pass the mentioned parameters through url-string.

Example 1:

```
from rmq_interface import RabbitMQInterface
interface = RabbitMQInterface('user', 'password', 'host', 'port')
```

Example 2:

```
from rmq_interface import RabbitMQInterface
interface = RabbitMQInterface(url_parameters='amqp://user:password@host:port')
```

## Sending a message

To send a message without blocking the running process (meaning you do not wait for the response), you call a `publish` method, which takes queue name and message payload as parameters.

Example:

```
interface.publish('queue_name', 'hello world')
```

If you need the synchronous call and receive the result before moving forward, use the `fetch` method. While it requires the same parameters as `publish`, `fetch` creates an anonymous auto-delete queue, where the worker will publish the response. Before the response has been received, the process is blocked. 

Example:

```
interface.fetch('queue_name', 'nice to meet you')

> nice to meet you too
```

You can specify the exchange if it differs from `amq.topic`. For the`publish` method, you can additionally specify the `reply_to` queue.

## Receiving messages

`listen` method makes the process subscribe to receive messages from the given queue. Messages are obtained and processed only in synchronous mode, meaning the process is idle until the next message comes.

`listen` method requires a *queue name* to subscribe for and the *consumer function*. Consumer function is called for every message received by the subscribed process. Consumer function has to take *message payload* (`str`) and *message properties*. The yielded result is published to the `reply_to` queue. 

To ease creating consumer functions, the framework introduces decorators `@rmq_interface.consumer_function` and `@rmq_inteface.class_consumer`. Each consumer function you use must be decorated with one of these features. The former decorator applies to the functions outside of classes, while the latter is designated for class methods only.

```
@rmq_interface.consumer_function
def func(body, properties):
    print(body, properties)
    return body

interface.listen('queue_name', func)

> b'1' <BasicProperties(['delivery_mode=1', 'headers={}'])>
> b'2' <BasicProperties(['delivery_mode=1', 'headers={}'])>
> b'3' <BasicProperties(['delivery_mode=1', 'headers={}'])>
> ...
```

Example 2 (class method): 

```
class processor:
    def __init__():
        pass
    
    @rmq_interface.class_consumer
    def func(self, body, properties):
        print(body, properties)
        return body

processor = Processor()
interface.listen('queue_name', processor.func)

> b'1' <BasicProperties(['delivery_mode=1', 'headers={}'])>
> b'2' <BasicProperties(['delivery_mode=1', 'headers={}'])>
> b'3' <BasicProperties(['delivery_mode=1', 'headers={}'])>
> ...
```
