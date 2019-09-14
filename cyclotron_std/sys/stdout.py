import sys
from collections import namedtuple

from cyclotron import Component

Sink = namedtuple('Sink', ['data'])


def make_driver():

    def driver(sink):
        def on_data_error(e):
            sys.stdout.write("error: {}".format(e))
            sys.stdout.flush()

        def on_data_completed():
            sys.stdout.flush()

        sink.data.subscribe(
            on_next=lambda data: sys.stdout.write(bytes(data, 'utf-8').decode('unicode_escape')),
            on_error=on_data_error,
            on_completed=on_data_completed)
        return None

    return Component(call=driver, input=Sink)
