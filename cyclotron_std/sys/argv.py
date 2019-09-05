import sys
from collections import namedtuple

import rx
from cyclotron import Component

Source = namedtuple('Source', ['argv'])


def make_driver(factory_scheduler=None):

    def driver(default_scheduler=None):
        scheduler = factory_scheduler or default_scheduler
        return Source(argv=rx.from_(sys.argv, scheduler=scheduler))

    return Component(call=driver)
