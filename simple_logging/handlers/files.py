from codecs import StreamReaderWriter, open
from pathlib import Path
from typing import Union

from .abc import Handler


class FileHandler(Handler):
    """
    The file handler writes output messages to a file.

    Args:
        - path (str or pathlib.Path): the file path
        - mode (str): the file handler's mode (defaults to "a" for append)
        - encodeing (str): the file's encoding (defaults to "utf-8")
    """

    def __init__(
        self, path: Union[str, Path], mode: str = "a", encoding: str = "utf-8"
    ) -> None:
        if isinstance(path, Path):
            path = str(path.resolve())
        self.path: str = path
        self.mode: str = mode
        self.encoding: str = encoding
        self.fh: StreamReaderWriter = open(self.path, self.mode, self.encoding)

    def write(self, message: str) -> None:
        """
        Writes the message to the configured file.

        Args:
            - message (str): the message to be written to the file
        """
        self.fh.write(message)
