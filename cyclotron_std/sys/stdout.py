import sys
from collections import namedtuple

from cyclotron import Component

Sink = namedtuple('Sink', ['data'])

def make_driver(loop = None):

    def stdout_driver(sink):
        sink.data.subscribe(lambda data: sys.stdout.write(bytes(data, 'utf-8').decode('unicode_escape')))
        return None

    return Component(call=stdout_driver, input=Sink)
