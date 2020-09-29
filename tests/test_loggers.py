import re
from io import StringIO

from simple_logging import Logger, LogLevel, StreamingHandler

handler = StreamingHandler(stream=StringIO())


def get_output():
    handler.stream.seek(0)
    output = handler.stream.read()
    handler.stream.seek(0)
    handler.stream.truncate(0)
    return output


def describe_level_setting():
    def method_level_lt_logger_level():  # pylint: disable=W0612
        logger = Logger("test", level=LogLevel.INFO, handler=handler)
        logger.debug("this shouldn't print")

        output = get_output()
        assert output == ""

    def method_level_gte_logger_level():  # pylint: disable=W0612
        logger = Logger("test", level=LogLevel.INFO, handler=handler)
        logger.info("this should print")

        output = get_output()
        assert re.match(
            r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{6} INFO test: this should print\n",
            output,
        )


def describe_non_standard_template_keys():
    def test_default_provided():  # pylint: disable=W0612
        logger = Logger("test", handler=handler, template="{foo}: {message}", foo="bar")
        logger.info("ok")

        output = get_output()
        assert output == "bar: ok\n"

    def test_value_provided_in_log_call():  # pylint: disable=W0612
        logger = Logger("test", handler=handler, template="{foo}: {message}")
        logger.info("ok", foo="baz")

        output = get_output()
        assert output == "baz: ok\n"

    def test_value_not_provided():  # pylint: disable=W0612
        logger = Logger("test", handler=handler, template="{foo}: {message}")
        logger.info("not provided")

        output = get_output()
        assert output == "\b: not provided\n"

    def test_value_is_callable():  # pylint: disable=W0612
        logger = Logger("test", handler=handler, template="{foo}: {message}")
        func = lambda: "yay!"

        logger.info("from lambda", foo=func)

        output = get_output()
        assert output == "yay!: from lambda\n"


def test_exception_capturing():
    logger = Logger("test", handler=handler, template="{level} {name}: {message}")

    try:
        1 / 0
    except ZeroDivisionError:
        logger.exception("caught")

    output = get_output()
    assert re.match(
        r"ERROR test: caught\nTraceback \(most recent call last\):\n  File .+\n    1 / 0\nZeroDivisionError: division by zero",
        output,
    )
