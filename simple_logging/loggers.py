import re
from datetime import datetime
from enum import IntEnum
from traceback import format_exc
from typing import Any, Dict, List, Optional

from .handlers.abc import Handler
from .handlers.streaming import StdOutHandler

keyname_regex = re.compile(r"(?:\{([a-zA-Z0-9_]+)\})")


class LogLevel(IntEnum):  # pylint: disable=C0115
    DEBUG = 0
    INFO = 1
    WARNING = 2
    ERROR = 3


class Logger:
    """
    A logger is the main interface to dumping information outputs. Loggers configure
    output templates and output handlers.

    Args:
        - name (str): the name of the logger (required)
        - level (LogLevel): the minimum logging level that this logger will
            output -- i.e. if set to INFO then debug message will not be output
            (defaults to INFO)
        - template (str): the output template (defaults to
            "{timestamp} {level} {name}: {message}")
        - handler (Handler): the handler this logger uses (defaults to StdOutHandler)
        - handlers (List[Handler]): a list of handlers this logger uses (default [])
        - ensure_new_lines (bool): should all outputs end with a new line?
            (defaults to True)

    Kwargs:
        Any keyword argument passed to the constructor will be used as a default
        value when formatting the template during a write. These values can be
        overwritten using the **overrides kwargs options in the logging methods.

    Examples:
        >>> from simple_logging import Logger
        >>> logger = Logger("example")
        >>> logger.info("this is an info level message")
        2020-09-29T12:39:06.125796 INFO example: this is an info level message

        >>> from simple_logging import Logger
        >>> from uuid import uuid4
        >>> logger = Logger("example", template="{timestamp} {level} {name} {uuid}: {message}", uuid=uuid4)
        >>> logger.info("uuid supplied by default value in init")
        2020-09-29T12:40:41.380675 INFO example c2e628dc-a97e-4537-841e-10fd08bed379: uuid supplied by default value in init

        >>> from simple_logging import Logger
        >>> from uuid import uuid4
        >>> logger = Logger("example", template="{timestamp} {level} {name} {uuid}: {message}", uuid=uuid4)
        >>> logger.info("uuid supplied in method call", uuid="i-was-overwritten")
        2020-09-29T12:41:10.975688 INFO example i-was-overwritten: uuid supplied in method call

        >>> from simple_logging import Logger
        >>> logger = Logger("example")
        >>> try:
        ...     1 / 0
        ... except ZeroDivisionError:
        ...     logger.exception("catching and logging the error")
        ...
        2020-09-29T12:44:36.871330 ERROR example: catching and logging the error
        Traceback (most recent call last):
          File ..., line ..., in ...
            1 / 0
        ZeroDivisionError: division by zero
    """

    _default_level = LogLevel.INFO
    _default_template = "{timestamp} {level} {name}: {message}"
    _default_handler = StdOutHandler()

    def __init__(
        self,
        name: str,
        level: LogLevel = _default_level,
        template: str = _default_template,
        handler: Optional[Handler] = None,
        handlers: Optional[List[Handler]] = None,
        ensure_new_lines: bool = True,
        **defaults,
    ) -> None:
        self.name: str = name
        self.level: LogLevel = level
        self.template: str = template
        self.ensure_new_lines: bool = ensure_new_lines

        self.handlers: List[Handler] = handlers or []
        if handler:
            self.handlers.append(handler)
        if not self.handlers:
            self.handlers = [self._default_handler]

        self.defaults: Dict[str, Any] = defaults

        self.keys = re.findall(keyname_regex, self.template)

    def __setattr__(self, name: str, value: Any) -> None:
        super().__setattr__(name, value)
        if name == "template":
            self.keys = re.findall(keyname_regex, self.template)

    def debug(self, message: str, **overrides) -> None:
        """
        Logs a debug level message.

        Args:
            - message (str): the message to be output

        Kwargs:
            Any keyword arguments passed to this method will either set or override
            the values used to format the output template.
        """
        self._log(LogLevel.DEBUG, message, **overrides)

    def info(self, message: str, **overrides) -> None:
        """
        Logs an info level message.

        Args:
            - message (str): the message to be output

        Kwargs:
            Any keyword arguments passed to this method will either set or override
            the values used to format the output template.
        """
        self._log(LogLevel.INFO, message, **overrides)

    def warning(self, message: str, **overrides) -> None:
        """
        Logs a warning level message.

        Args:
            - message (str): the message to be output

        Kwargs:
            Any keyword arguments passed to this method will either set or override
            the values used to format the output template.
        """
        self._log(LogLevel.WARNING, message, **overrides)

    def error(self, message: str, **overrides) -> None:
        """
        Logs an error level message.

        Args:
            - message (str): the message to be output

        Kwargs:
            Any keyword arguments passed to this method will either set or override
            the values used to format the output template.
        """
        self._log(LogLevel.ERROR, message, **overrides)

    def exception(self, message: str, **overrides) -> None:
        """
        Logs an error level message and appends the exception stack trace to the message.

        Args:
            - message (str): the message to be output

        Kwargs:
            Any keyword arguments passed to this method will either set or override
            the values used to format the output template.
        """
        message = f"{message}\n{format_exc()}"
        self._log(LogLevel.ERROR, message, **overrides)

    def _log(self, level: LogLevel, message: str, **overrides) -> None:
        if level < self.level:
            return

        kwargs = {
            key: value() if callable(value) else value
            for key, value in self.defaults.items()
        }

        kwargs["message"] = message

        timestamp = overrides.pop("timestamp", None)
        kwargs["timestamp"] = timestamp or datetime.now().isoformat()

        _level = overrides.pop("level", None)
        kwargs["level"] = _level or level.name

        name = overrides.pop("name", None)
        kwargs["name"] = name or self.name

        kwargs.update(
            **{
                key: value() if callable(value) else value
                for key, value in overrides.items()
            }
        )

        for key in self.keys:
            if key not in kwargs:
                kwargs[key] = "\b"

        for handler in self.handlers:
            output = self.template.format(**kwargs)
            if self.ensure_new_lines and not output.endswith("\n"):
                output += "\n"
            handler.write(output)
