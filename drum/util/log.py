from logging import (
    CRITICAL,
    DEBUG,
    ERROR,
    FATAL,
    INFO,
    WARN,
    WARNING,
    FileHandler,
    Formatter,
    Handler,
    StreamHandler,
    getLogger,
)
from typing import Optional

LOG_LEVELS = dict(
    CRITICAL=CRITICAL,
    FATAL=FATAL,
    ERROR=ERROR,
    WARNING=WARNING,
    WARN=WARN,
    INFO=INFO,
    DEBUG=DEBUG,
)


def setup_logger(
    name: str,
    logfile: Optional[str] = None,
    console: bool = False,
    log_level: int | str = DEBUG,
) -> None:
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

    if isinstance(log_level, str):
        log_level = LOG_LEVELS[log_level.upper()]

    logger.setLevel(log_level)

    for handler in handlers:
        logger.addHandler(handler)
