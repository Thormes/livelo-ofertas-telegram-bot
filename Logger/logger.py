import logging
from logging import Logger, handlers, Formatter
import os
import json

os.makedirs('log', exist_ok=True)

loggers = {}


def get_logger(name: str, file: str = 'app.log', level=logging.INFO) -> Logger:
    global loggers

    if loggers.get(name):
        return loggers.get(name)

    handler = handlers.RotatingFileHandler(
        filename=os.path.join("./log/", file),
        maxBytes=1024 * 1024 * 10,
        backupCount=10,
        encoding="UTF-8")

    formato = '[%(asctime)s] [%(name)s] [%(levelname)s] [%(message)s]'
    formatter = Formatter(formato, datefmt='%Y-%m-%d %H:%M:%S')
    handler.setFormatter(formatter)
    logger = logging.getLogger(name)
    logger.addHandler(handler)
    logger.setLevel(level)
    loggers[name] = logger
    return logger
