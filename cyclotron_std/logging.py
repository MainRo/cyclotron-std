from collections import namedtuple
from rx import Observable
import logging
from cyclotron import Component


Sink = namedtuple('Sink', ['request'])
Source = namedtuple('Source', ['response'])

# Sink items
SetLevel = namedtuple('SetLevel', ['logger', 'level'])
Log = namedtuple('Log', ['logger', 'level', 'message'])

# Sink and Source items
SetLevelDone = namedtuple('SetLevelDone', [])

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
    handlers = {}
    observer = None
    def driver(sink):
        def on_subscribe(o):
            nonlocal observer
            observer = o

        def on_request_item(i):
            nonlocal handlers
            nonlocal observer
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
            elif type(i) is SetLevelDone:
                if observer is not None:
                    observer.on_next(i)
            else:
                if observer is not None:
                    observer.on_error("invalid item: {}".format(i))

        sink.request.subscribe(on_request_item)
        return Source(response=Observable.create(on_subscribe))

    return Component(call=driver, input=Sink)