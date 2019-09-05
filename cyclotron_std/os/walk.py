import os
from collections import namedtuple

import rx
import rx.operators as ops
from rx.subject import Subject
from cyclotron import Component

Sink = namedtuple('Sink', ['request'])
Source = namedtuple('Source', ['response'])

# Sink items
Walk = namedtuple('Walk', ['top', 'id', 'recursive'])
Walk.__new__.__defaults__ = (False,)

# Source items
WalkResponse = namedtuple('WalkResponse', ['top', 'id', 'content'])
DirItem = namedtuple('DirItem', ['top', 'directories', 'files'])


def walk(top, recursive, scheduler):

    dirnames = []
    filenames = []
    for path, dirs, files in os.walk(top):
        for filename in files:
            filenames.append(os.path.join(path, filename))
        if recursive is True:
            for dirname in dirs:
                dirnames.append(walk(os.path.join(path, dirname), recursive, scheduler))

    return DirItem(
        top=top,
        directories=rx.from_(dirnames, scheduler=scheduler),
        files=rx.from_(filenames, scheduler=scheduler))


def make_driver(factory_scheduler=None):

    def driver(sink, default_scheduler=None):
        driver_scheduler = factory_scheduler or default_scheduler

        def subscribe_response(observer, scheduler):
            def on_request_item(i):
                if type(i) is Walk:
                    content = walk(i.top, i.recursive, driver_scheduler)
                    observer.on_next(WalkResponse(
                        top=i.top, id=i.id,
                        content=content))

            sink.request.subscribe(on_request_item)

        return Source(response=rx.create(subscribe_response))

    return Component(call=driver, input=Sink)


Api = namedtuple('Api', ['walk'])
Adapter = namedtuple('Adapter', ['sink', 'api'])


def adapter(source):
    sink_request = Subject()

    def walk(top, recursive=False):
        def on_subscribe(observer, scheduler):
            response = source.pipe(
                ops.filter(lambda i: i.id is response_observable),
                ops.take(1),
                ops.map(lambda i: i.content),
            )

            dispose = response.subscribe(observer)
            sink_request.on_next(Walk(
                id=response_observable,
                top=top,
                recursive=recursive,
            ))

            return dispose

        response_observable = rx.create(on_subscribe)
        return response_observable

    return Adapter(
        sink=sink_request,
        api=Api(
            walk=walk,
        )
    )
