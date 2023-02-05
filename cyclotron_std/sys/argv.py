import sys
from collections import namedtuple

import reactivex as rx
from cyclotron import Component

Source = namedtuple('Source', ['argv'])


def make_driver(scheduler=None):

    def driver():
        return Source(argv=rx.from_(sys.argv, scheduler=scheduler))

    return Component(call=driver)
