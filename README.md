# RabbitMQ Interface

Обертка над библиотекой pika, предоставляющая возможность взаимодействовать с очередью сообщений RabbitMQ легко и быстро.

**Автор и разработчик:**

- Еремеев Максим (@m.eremeev)

## Особенности реализации

- Язык - ```Python 3.6```
- Библиотеки: ```pika``` (основная библиотека взаимодействия с RabbitMQ).


## Установка

```
cd platform/rmq_interface
sudo python setup.py build
sudo python setup.py install
```

## Подключение к RabbitMQ

Вся функциональность содержится в объекте ```rmq_interface```.  При его создании необходимо указать имя пользователя, пароль, хост и порт для подключения или единую url-строку.

Пример 1:

```
from rmq_interface import rmq_interface
interface = rmq_interface.RabbitMQInterface('user', 'password', 'host', 'port')
```

Пример 2:

```
from rmq_interface import rmq_interface
interface = rmq_interface.RabbitMQInterface(url_parameters='amqp://user:password@host:port')
```

## Отправка сообщения

Для отправки сообщения без ожидания ответа (асинхронный режим) необходимо вызвать метод ```publish``` , передав ему имя очереди и строку сообщения.

Пример:

```
interface.publish('queue_name', 'hello world')
```

Если ответа необходимо дождаться (синхронный режим), необходимо использовать метод ```fetch```  с аналогичными параметрами. Метод создаст анонимную очередь, куда передаст ответ, который и вернет метод. При этом, до получения ответа, процесс будет заблокирован.

Пример:

```
interface.fetch('queue_name', 'nice to meet you')

> nice to meet you too
```

Возможно дополнительно указать  ```exchange``` для отправки сообщений, если он отличается от ```amq.topic```. Для метода ```publish``` можно передать параметр ```reply_to```.

## Получение сообщений

Библиотека предоставляет возможность получения сообщений в синхронном режиме. Вызывая метод  ```listen```, процесс подписывается на сообщения из конкретной очереди. Пока сообщений в очереди нет, проуесс блокируется. 
Метод ```listen``` принимает имя очереди для подписки и функцию-обработчик для сообщений. Функция-обработчик вызывается для каждого сообщения из очереди при его появлении. Функция обработчик должна принимать текст сообщения (```str```) и параметры сообщения, возвращать результат, который отправляется в ```reply_to``` для данного запроса. Для корректной работы с очередью6 каждая функция-обработчик должна быть обрамлена декоратором ```@rmq_interface.consumer_function```  или  ```@rmq_interface.class_consumer```. Первый вариант подходит для функций вне классов, второй - только для методов классов.

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

Пример 2 (метод класса): 

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
