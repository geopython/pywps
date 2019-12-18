import logging


def get_logger(file=None, level=None, format=None):
    level = level or 'WARNING'
    format = format or '%(asctime)s] [%(levelname)s] file=%(pathname)s line=%(lineno)s module=%(module)s function=%(funcName)s %(message)s'  # noqa
    logger = logging.getLogger('PYWPS')
    if file:
        logger.setLevel(getattr(logging, level))
        if not logger.hasHandlers():
            fh = logging.FileHandler(file)
            fh.setFormatter(logging.Formatter(format))
            logger.addHandler(fh)
    else:  # NullHandler | StreamHandler
        if not logger.hasHandlers():
            logger.addHandler(logging.NullHandler())
    return logger
