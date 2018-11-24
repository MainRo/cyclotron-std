import os
from collections import namedtuple

from rx import Observable, AnonymousObservable
from rx.subjects import Subject
from cyclotron import Component

Sink = namedtuple('Sink', ['request'])
Source = namedtuple('Source', ['response'])

# Sink items
Walk = namedtuple('Walk', ['top', 'id', 'recursive'])
Walk.__new__.__defaults__ = (False,)

# Source items
WalkResponse = namedtuple('WalkResponse', ['top', 'id', 'content'])
DirItem = namedtuple('DirItem', ['top', 'directories', 'files'])


def walk(top, recursive):

    dirnames = []
    filenames = []
    for path, dirs, files in os.walk(top):
        for filename in files:
            filenames.append(os.path.join(path, filename))
        if recursive is True:
            for dirname in dirs:
                dirnames.append(walk(os.path.join(path, dirname), recursive))

    return DirItem(
        top=top,
        directories=Observable.from_(dirnames),
        files=Observable.from_(filenames))


def make_driver(loop=None):

    def driver(sink):
        def subscribe_response(observer):
            def on_request_item(i):
                if type(i) is Walk:
                    content = walk(i.top, i.recursive)
                    observer.on_next(WalkResponse(
                        top=i.top, id=i.id,
                        content=content))

            sink.request.subscribe(on_request_item)

        return Source(response=AnonymousObservable(subscribe_response))

    return Component(call=driver, input=Sink)


Api = namedtuple('Api', ['walk'])
Adapter = namedtuple('Adapter', ['sink', 'api'])


def adapter(source):
    sink_request = Subject()

    def walk(top, recursive=False):
        def on_subscribe(observer):
            response = (
                source
                .filter(lambda i: i.id is response_observable)
                .take(1)
                .map(lambda i: i.content)
            )

            dispose = response.subscribe(observer)
            sink_request.on_next(Walk(
                id=response_observable,
                top=top,
                recursive=recursive,
            ))

            return dispose

        response_observable = Observable.create(on_subscribe)
        return response_observable

    return Adapter(
        sink=sink_request,
        api=Api(
            walk=walk,
        )
    )
