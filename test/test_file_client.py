from collections import namedtuple
import functools
from unittest import TestCase

from rx import Observable
from rx.subjects import Subject
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

    def test_read(self):
        driver_response = Subject()

        file_adapter = file.adapter(driver_response)

        file_adapter.sink.subscribe(
            on_next=functools.partial(self.on_next, 'driver_request'),
            on_error=functools.partial(self.on_error, 'driver_request'),
            on_completed=functools.partial(self.on_completed, 'driver_request'))

        response = file_adapter.api.read('/foo.txt')

        response.subscribe(
            on_next=functools.partial(self.on_next, 'response'),
            on_error=functools.partial(self.on_error, 'response'),
            on_completed=functools.partial(self.on_completed, 'response'))

        self.assertEqual(
            file.Read(id=response, 
                path='/foo.txt',
                size=-1, mode='r',
            ),
            self.actual['driver_request']['next'][0])

        result = file.ReadResponse(id=response, path='a', data=Observable.just(b'bar'))
        driver_response.on_next(result)

        self.assertIs(
            b'bar',
            self.actual['response']['next'][0])
