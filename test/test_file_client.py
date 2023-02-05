import functools
from unittest import TestCase

import reactivex as rx
import reactivex.operators as ops
from reactivex.subject import Subject
import cyclotron_std.io.file as file


class FileClientTestCase(TestCase):
    def setUp(self):
        self.actual = {}

    def create_actual(self):
        return {
            'next': [],
            'error': None,
            'completed': False
        }

    def on_next(self, key, i):
        if not key in self.actual:
            self.actual[key] = self.create_actual()
        self.actual[key]['next'].append(i)

    def on_error(self, key, e):
        if not key in self.actual:
            self.actual[key] = self.create_actual()
        self.actual[key]['error'] = e

    def on_completed(self, key):
        if not key in self.actual:
            self.actual[key] = self.create_actual()
        self.actual[key]['completed'] = True  

    def test_read_data(self):
        driver_response = Subject()

        read_request = rx.just(file.Read(id=1, path='/foo.txt', size=-1, mode='r'))

        driver_request, read_response = read_request.pipe(file.read(driver_response))

        driver_request.subscribe(
            on_next=functools.partial(self.on_next, 'driver_request'),
            on_error=functools.partial(self.on_error, 'driver_request'),
            on_completed=functools.partial(self.on_completed, 'driver_request'))

        read_response.pipe(ops.flat_map(lambda i: i.data)).subscribe(
            on_next=functools.partial(self.on_next, 'response'),
            on_error=functools.partial(self.on_error, 'response'),
            on_completed=functools.partial(self.on_completed, 'response'))

        self.assertEqual(
            file.Context(
                id=read_request,
                observable=read_request
            ),
            self.actual['driver_request']['next'][0])

        result = file.Context(
            id=read_request,
            observable=rx.just(file.ReadResponse(id=1, path='/foo.txt', data=rx.just(b'bar')))
        )
        driver_response.on_next(result)

        self.assertIs(
            b'bar',
            self.actual['response']['next'][0])
