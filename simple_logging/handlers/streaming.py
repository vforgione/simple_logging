from io import TextIOWrapper
from sys import stderr, stdout

from .abc import Handler


class StreamingHandler(Handler):
    """
    A streaming halder writes output messages to a stream -- typically STDOUT or
    STDERR. However, it can be to anything that looks like a stream; i.e.
    an instance of io.StringIO.

    Args:
        - stream (TextIOWrapper): the output stream that writes the messages
    """

    def __init__(self, stream: TextIOWrapper) -> None:
        self.stream: TextIOWrapper = stream

    def write(self, message: str) -> None:
        """
        Writes the message to the configured stream.

        Args:
            - message (str): the message to be written to the stream
        """
        self.stream.write(message)


class StdOutHandler(StreamingHandler):  # coverage: disable
    """
    A convenience class that uses STDOUT as the output stream.
    """

    def __init__(self):
        super().__init__(stream=stdout)


class StdErrHandler(StreamingHandler):  # coverage: disable
    """
    A convenience class that uses STDERR as the output stream.
    """

    def __init__(self):
        super().__init__(stream=stderr)
