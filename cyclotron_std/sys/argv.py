import sys
from collections import namedtuple

from rx import Observable
from cyclotron import Component

Source = namedtuple('Source', ['argv'])

def make_driver(loop = None):

    def argv_driver():
        return Source(argv=Observable.from_(sys.argv))

    return Component(call=argv_driver)
