import os
from collections import namedtuple

import reactivex as rx
import reactivex.operators as ops
from reactivex.subject import Subject
from cyclotron import Component

Sink = namedtuple('Sink', ['request'])
Source = namedtuple('Source', ['response'])

# Sink items
Walk = namedtuple('Walk', ['top', 'id', 'recursive'])
Walk.__new__.__defaults__ = (False,)

# Source items
WalkResponse = namedtuple('WalkResponse', ['top', 'id', 'content'])
DirItem = namedtuple('DirItem', ['top', 'directories', 'files'])


def _walk(top, recursive, scheduler):

    dirnames = []
    filenames = []
    for path, dirs, files in os.walk(top):
        for filename in files:
            filenames.append(os.path.join(path, filename))
        if recursive is True:
            for dirname in dirs:
                dirnames.append(_walk(os.path.join(path, dirname), recursive, scheduler))

    return DirItem(
        top=top,
        directories=rx.from_(dirnames, scheduler=scheduler),
        files=rx.from_(filenames, scheduler=scheduler))


def make_driver():
    def driver(sink):
        def subscribe_response(observer, scheduler):
            def on_request_item(i):
                if type(i) is Walk:
                    content = _walk(i.top, i.recursive, scheduler)
                    observer.on_next(WalkResponse(
                        top=i.top, id=i.id,
                        content=content))

            sink.request.subscribe(on_request_item)

        return Source(response=rx.create(subscribe_response))

    return Component(call=driver, input=Sink)
