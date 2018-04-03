import sys
from cyclotron import Component

Sink = namedtuple('Sink', ['data'])

def make_stdout_driver(loop = None):

    def stdout_driver(sink):
        sink.data.subscribe(lambda data: sys.stdout.write(data))
        return None

    return Component(entry_point=stdout_driver, input=Sink)
