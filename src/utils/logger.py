import colorlog
import logging
try:
    import colorlog
except ImportError:
    colorlog = None

def setup_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """
    Create a colored and formatted logger.

    Args:
        name (str): Logger name
        level (int): Logging level

    Returns:
        logging.Logger: Configured logger
    """
    if colorlog is not None:
        logger = colorlog.getLogger(name)
        handler = colorlog.StreamHandler()
        handler.setFormatter(colorlog.ColoredFormatter(
            '%(log_color)s%(levelname)s:%(name)s:%(message)s',
            log_colors={
                'DEBUG': 'cyan',
                'INFO': 'green',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'red,bg_white',
            }
        ))
    else:
        logger = logging.getLogger(name)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(levelname)s:%(name)s:%(message)s')
        handler.setFormatter(formatter)

    logger.addHandler(handler)
    logger.setLevel(level)
    logger.propagate = False

    return logger