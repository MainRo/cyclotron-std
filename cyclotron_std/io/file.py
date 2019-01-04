import os
import functools
from collections import namedtuple

from rx import Observable
from rx.subjects import Subject
from cyclotron import Component


Sink = namedtuple('Sink', ['request'])
Source = namedtuple('Source', ['response'])

# Sink items
Context = namedtuple('Context', ['id', 'observable'])
Read = namedtuple('Read', ['id', 'path', 'size', 'mode'])
Read.__new__.__defaults__ = (-1, 'r',)
Write = namedtuple('Write', ['id', 'path', 'data', 'mode', 'mkdirs'])
Write.__new__.__defaults__ = ('w', False,)
ReadLine = namedtuple('ReadLine', ['id', 'path'])

# Source items
ReadResponse = namedtuple('ReadResponse', ['id', 'path', 'data'])
WriteResponse = namedtuple('WriteResponse', ['id', 'path', 'status'])


def make_driver(loop=None):
    def driver(sink):
        """ File driver.
        Reads content of files provided in sink stream and outputs it in the
        source stream.
        warning: implementation is synchronous.

        @todo : This driver should return a stream of streams so that the
        content of each file end with a stream completion. For now each "data"
        stream ends once the first file content is read.

        sink stream structure:
        - name: identifier of the file
        - path: path of the file to read

        source stream structure;
        - name: identifier of the file
        - data: content of the file
        """
        def on_context_subscribe(sink, observer):
            def on_next(i):
                if type(i) is Read:
                    try:
                        with open(i.path, i.mode) as content_file:
                            content = content_file.read(i.size)
                            data = Observable.just(content)
                            observer.on_next(ReadResponse(
                                id=i.id, path=i.path, data=data))
                    except Exception as e:
                        observer.on_next(Observable.throw(e))
                elif type(i) is ReadLine:
                    try:
                        with open(i.path) as content_file:
                            data = Observable.from_(content_file)
                            observer.on_next(ReadResponse(
                                id=i.id, path=i.path, data=data))
                    except Exception as e:
                        observer.on_next(Observable.throw(e))
                elif type(i) is Write:
                    try:
                        if i.mkdirs is True:
                            os.makedirs(os.path.split(i.path)[0], exist_ok=True)
                        with open(i.path, i.mode) as content_file:
                            size = content_file.write(i.data)
                            status = 0 if size == len(i.data) else -1
                            observer.on_next(WriteResponse(
                                id=i.id, path=i.path, status=status))
                    except Exception as e:
                        observer.on_next(Observable.throw(e))
                else:
                    observer.on_error("file unknown command: {}".format(i))

            sink.subscribe(
                on_next=on_next,
                on_completed=observer.on_completed,
                on_error=observer.on_error
            )

        def on_subscribe(observer):

            def on_request_item(i):
                if type(i) is Context:
                    observer.on_next(
                        Context(i.id, Observable.create(functools.partial(
                            on_context_subscribe,
                            i.observable)))
                    )
                elif type(i) is Read:
                    with open(i.path, i.mode) as content_file:
                        content = content_file.read(i.size)
                        data = Observable.just(content)
                        observer.on_next(ReadResponse(
                            id=i.id, path=i.path, data=data))
                elif type(i) is ReadLine:
                    content_file = open(i.path)
                    data = Observable.from_(content_file)
                    observer.on_next(ReadResponse(
                        id=i.id, path=i.path, data=data))
                elif type(i) is Write:
                    if i.mkdirs is True:
                        os.makedirs(os.path.split(i.path)[0], exist_ok=True)
                    with open(i.path, i.mode) as content_file:
                        size = content_file.write(i.data)
                        status = 0 if size == len(i.data) else -1
                        observer.on_next(WriteResponse(
                            id=i.id, path=i.path, status=status))
                else:
                    observer.on_error("file unknown command: {}".format(i))

            def on_request_error(e):
                observer.on_error(e)

            def on_request_completed():
                observer.on_completed()

            dispose = sink.request.subscribe(
                on_next=on_request_item,
                on_error=on_request_error,
                on_completed=on_request_completed)

            return dispose

        return Source(
            response=Observable.create(on_subscribe),
        )

    return Component(call=driver, input=Sink)


Api = namedtuple('Api', ['read', 'write'])
Adapter = namedtuple('Adapter', ['sink', 'api'])


def adapter(source):
    sink_request = Subject()

    def read(path, size=-1, mode='r'):
        def on_subscribe(observer):
            response = (
                source
                .filter(lambda i: i.id is response_observable)
                .take(1)
                .flat_map(lambda i: i.data)
            )

            dispose = response.subscribe(observer)
            sink_request.on_next(Read(
                id=response_observable,
                path=path,
                size=size,
                mode=mode,
            ))

            return dispose

        response_observable = Observable.create(on_subscribe)
        return response_observable

    def write(path, data, mode='w', mkdirs=False):
        def on_subscribe(observer):
            response = (
                source
                .filter(lambda i: i.id is response_observable)
                .take(1)
                .map(lambda i: i.status)
            )

            dispose = response.subscribe(observer)
            sink_request.on_next(Write(
                id=response_observable,
                path=path,
                data=data,
                mode=mode,
                mkdirs=mkdirs)
            )

            return dispose

        response_observable = Observable.create(on_subscribe)
        return response_observable

    return Adapter(
        sink=sink_request,
        api=Api(
            read=read,
            write=write,
        )
    )
