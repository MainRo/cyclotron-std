from collections import namedtuple
import logging
from cyclotron import Component


Sink = namedtuple('Sink', ['request'])

# Sink items
SetLevel = namedtuple('SetLevel', ['logger', 'level'])
Log = namedtuple('Log', ['logger', 'level', 'message'])


def level_from_string(level):
    if level == 'DEBUG':
        return 10
    elif level == 'INFO':
        return 20
    elif level == 'WARNING':
        return 30
    elif level == 'CRITICAL':
        return 50
    else:
        return 40


def make_driver():
    def driver(sink):
        handlers = {}

        def on_next(i):
            nonlocal handlers
            if type(i) is Log:
                logging.getLogger(i.logger).log(i.level, i.message)
            elif type(i) is SetLevel:
                level = level_from_string(i.level)
                logger = logging.getLogger(i.logger)
                logger.setLevel(level)
                if i.logger in handlers:
                    logger.removeHandler(handlers[i.logger])    
                handlers[i.logger] = logging.StreamHandler()
                handlers[i.logger].setLevel(level)
                logger.addHandler(handlers[i.logger])

        sink.request.subscribe(on_next)
        return None

    return Component(call=driver, input=Sink)
