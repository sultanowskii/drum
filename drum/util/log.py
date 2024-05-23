from logging import DEBUG, FileHandler, Formatter, Handler, StreamHandler, getLogger
from typing import Optional


def setup_logger(name: str, logfile: Optional[str] = None, console: bool = False) -> None:
    """Sets up logger with specific name."""
    if logfile is None:
        _logfile = f'{name}.log'
    else:
        _logfile = logfile

    handlers: list[Handler] = []

    formatter = Formatter(fmt='%(levelname)s\t%(module)s:%(funcName)s\t%(message)s')

    if console:
        console_handler = StreamHandler()
        console_handler.setFormatter(formatter)
        handlers.append(console_handler)

    file_handler = FileHandler(_logfile, mode='w')
    file_handler.setFormatter(formatter)
    handlers.append(file_handler)

    logger = getLogger(name)
    logger.setLevel(DEBUG)

    for handler in handlers:
        logger.addHandler(handler)
