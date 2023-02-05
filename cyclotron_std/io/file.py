import os
import functools
from collections import namedtuple

import reactivex as rx
import reactivex.operators as ops
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


def make_driver():

    def driver(sink):
        """ File driver.
        Reads content of files provided in sink stream and outputs it in the
        source stream.
        warning: implementation is synchronous.

        sink stream structure:
        - name: identifier of the file
        - path: path of the file to read

        source stream structure;
        - name: identifier of the file
        - data: content of the file
        """
        def on_context_subscribe(sink, observer, scheduler):
            def on_next(i):
                if type(i) is Read:
                    try:
                        with open(i.path, i.mode) as content_file:
                            content = content_file.read(i.size)
                            data = rx.just(content)
                    except Exception as e:
                        data = rx.throw(e)

                    observer.on_next(ReadResponse(
                        id=i.id, path=i.path, data=data))
                elif type(i) is ReadLine:
                    try:
                        with open(i.path) as content_file:
                            ''' from_ does not work with ImmediateScheduler
                            def on_data_subscribe(data_observer):
                                for line in content_file:
                                    data_observer.on_next(line)
                                data_observer.on_completed()

                            data = Observable.create(on_data_subscribe)
                            '''
                            data = rx.from_(content_file)
                    except Exception as e:
                        data = rx.throw(e)

                    observer.on_next(ReadResponse(
                        id=i.id, path=i.path, data=data))
                elif type(i) is Write:
                    try:
                        if i.mkdirs is True:
                            os.makedirs(os.path.split(i.path)[0], exist_ok=True)
                        with open(i.path, i.mode) as content_file:
                            size = content_file.write(i.data)
                            status = 0 if size == len(i.data) else -1

                    except Exception as e:
                        status = e

                    observer.on_next(WriteResponse(
                        id=i.id, path=i.path, status=status))

                else:
                    observer.on_error("file unknown command: {}".format(i))

            sink.subscribe(
                on_next=on_next,
                on_completed=observer.on_completed,
                on_error=observer.on_error
            )

        def on_subscribe(observer, scheduler):
            def on_request_item(i):
                if type(i) is Context:
                    observer.on_next(
                        Context(i.id, rx.create(functools.partial(
                            on_context_subscribe,
                            i.observable)))
                    )

                else:
                    observer.on_error("file unknown command: {}".format(i))

            dispose = sink.request.subscribe(
                on_next=on_request_item,
                on_error=observer.on_error,
                on_completed=observer.on_completed)

            return dispose

        return Source(
            response=rx.create(on_subscribe),
        )

    return Component(call=driver, input=Sink)


def read(driver_response):
    def _read(read_request):

        driver_request = rx.just(
                Context(id=read_request, observable=read_request)
            )

        read_response = driver_response.pipe(
            ops.filter(lambda i: i.id is read_request),
            ops.flat_map(lambda i: i.observable)
        )
        return driver_request, read_response

    return _read
