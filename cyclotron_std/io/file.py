import os
from collections import namedtuple

from rx import Observable, AnonymousObservable
from cyclotron import Component

Sink = namedtuple('Sink', ['request'])
Source = namedtuple('Source', ['response'])

# Sink items
Read = namedtuple('Read', ['id', 'path', 'size'])
Read.__new__.__defaults__ = (-1,)

# Source items
ReadResponse = namedtuple('ReadResponse', ['id', 'path', 'data'])


def make_driver(loop=None):
    def driver(sink):
        """ File driver.
        Reads content of files provided in sink stream and outputs it in the source
        stream.
        warning: implementation is synchronous.

        @todo : This driver should return a stream of streams so that the content
        of each file end with a stream completion. For now each "data" stream ends
        once the first file content is read.

        sink stream structure:
        - name: identifier of the file
        - path: path of the file to read

        source stream structure;
        - name: identifier of the file
        - data: content of the file
        """
        def subscribe_data(observer):

            def on_request_item(i):
                if type(i) is Read:
                    with open(i.path, 'r') as content_file:
                        content = content_file.read(i.size)
                        data = Observable.just(content)
                        observer.on_next(ReadResponse(id=i.id, path=i.path, data=data))
                else:
                    observer.on_error("file unknown command: {}".format(i))

            def on_request_error(e):
                observer.on_error(e)

            def on_request_completed():
                observer.on_completed()

            sink.request.subscribe(
                on_next=on_request_item,
                on_error=on_request_error,
                on_completed=on_request_completed)

        return Source(
            response=AnonymousObservable(subscribe_data),
        )

    return Component(call=driver, input=Sink)
