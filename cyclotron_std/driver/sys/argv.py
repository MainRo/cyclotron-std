
import sys
from collections import namedtuple
from cyclotron import Component

Source = namedtuple('Source', ['argv'])

def make_argv_driver(loop = None):

    def argv_driver():
        return Source(argv=Observable.from_(sys.argv))

    return Component(entry_point=argv_driver, output=Source)
