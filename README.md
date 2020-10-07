# Simple Logging

Finally, a Python logging library that doesn't make you want to destroy all technology and spend the rest of your days foraging in the woods and fighting herds of squirrels for shelter.

## Usage

Simple logging aims to be intuitive and unobstrusive. It's also extremely flexible in producing logged information.

```python
from simple_logging import Logger

logger = Logger("example")
logger.info("this is an info level message")
# 2020-09-29T12:39:06.125796 INFO example: this is an info level message
```

The default template is:

```python
"{timestamp} {level} {name}: {message}"
```

You can provide additional key-values in the template. Those values can either be static or generated by a callable:

```python
from simple_logging import Logger
from uuid import uuid4

static_logger = Logger("example", template="{timestamp} {level} {name} {uuid}: {message}", uuid=uuid4)
static_logger.info("uuid supplied by default value in init")
# 2020-09-29T12:40:41.380675 INFO example c2e628dc-a97e-4537-841e-10fd08bed379: uuid supplied by default value in init

callable_logger = Logger("example", template="{timestamp} {level} {name} {uuid}: {message}", uuid=uuid4)
callable_logger.info("uuid supplied in method call", uuid="i-was-overwritten")
# 2020-09-29T12:41:10.975688 INFO example i-was-overwritten: uuid supplied in method call
```

And like the stdlib logger, you can log exceptions from the current context:

```python
from simple_logging import Logger

logger = Logger("example")
try:
    1 / 0
except ZeroDivisionError:
    logger.exception("catching and logging the error")
# 2020-09-29T12:44:36.871330 ERROR example: catching and logging the error
# Traceback (most recent call last):
#   File ..., line ..., in ...
#     1 / 0
# ZeroDivisionError: division by zero
```
