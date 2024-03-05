import logging
import sys


def get_logger(level: int = logging.DEBUG, turn_off_another_logs: bool = False):
    """
    Configures and returns a custom logger with colored output.

    :param level: Logging level for the logger (default is logging.DEBUG).
    :param turn_off_another_logs: If True, turns off logging for all other loggers (default is False).
    :return: Configured logger instance.
    """

    class ColoredFormatter(logging.Formatter):
        green = "\033[92m"
        blue = "\033[94m"
        yellow = "\x1b[33;20m"
        red = "\x1b[31;20m"
        bold_red = "\x1b[31;1m"
        reset = "\x1b[0m"

        _formats = {
            logging.DEBUG: f"{blue}%(levelname)s{reset}:\t%(message)s",
            logging.INFO: f"{green}%(levelname)s{reset}:\t%(message)s",
            logging.WARNING: f"{yellow}%(levelname)s{reset}:\t%(message)s",
            logging.ERROR: f"{red}%(levelname)s{reset}:\t%(message)s",
            logging.CRITICAL: f"{bold_red}%(levelname)s{reset}:\t%(message)s"
        }

        def format(self, record):
            log_fmt = self._formats.get(record.levelno)
            formatter = logging.Formatter(log_fmt)
            return formatter.format(record)

    if turn_off_another_logs:
        for lg in [logging.getLogger(name) for name in logging.root.manager.loggerDict]:
            lg.handlers = []
            lg.propagate = False

    _logger = logging.getLogger(__name__)
    _logger.setLevel(logging.DEBUG)

    handler = logging.StreamHandler(stream=sys.stdout)
    handler.setFormatter(ColoredFormatter())

    _logger.addHandler(handler)
    _logger.setLevel(level)

    return _logger


logger = get_logger()
