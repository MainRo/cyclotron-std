from unittest import TestCase
import tempfile
import os
import shutil

import reactivex as rx
import reactivex.operators as ops
from reactivex import Observer

import cyclotron_std.os.walk as walk


def create_file_tree(workdir, directories, files):
    for directory in directories:
        os.makedirs(os.path.join(workdir, directory))

    for f in files:
        open(os.path.join(workdir, f), 'a').close()


class OsWalkTestCase(TestCase):

    def setUp(self):
        self.wordkir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.wordkir)

    def test_create(self):
        source = walk.make_driver().call(walk.Sink(request=rx.empty()))
        self.assertIsNotNone(source)

    def test_walk_file(self):

        expected_files = ['foo', 'bar', 'biz']
        actual_files = []
        create_file_tree(self.wordkir, [], expected_files)
        source = walk.make_driver().call(walk.Sink(request=rx.just(
            walk.Walk(top=self.wordkir, id='test')
        )))

        class TestObserver(Observer):
            def on_next(self, i):
                actual_files.append(i)

            def on_completed(self):
                return

            def on_error(self, e):
                raise Exception(e)

        source.response.pipe(
            ops.filter(lambda i: type(i) is walk.WalkResponse),
            ops.flat_map(lambda i: i.content.files),
        ).subscribe(TestObserver())

        for f in expected_files:
            self.assertIn(os.path.join(self.wordkir, f), actual_files)

    def test_walk_dir(self):

        expected_files = []
        expected_dirs = ['dfoo', 'dbar', 'dbiz']
        actual_files = []
        actual_dirs = []
        create_file_tree(self.wordkir, expected_dirs, expected_files)
        source = walk.make_driver().call(walk.Sink(request=rx.just(
            walk.Walk(top=self.wordkir, id='test', recursive=True)
        )))

        class TestObserver(Observer):
            def on_next(self, i):
                actual_dirs.append(i.top)

            def on_completed(self):
                return

            def on_error(self, e):
                raise Exception(e)

        source.response.pipe(
            ops.filter(lambda i: type(i) is walk.WalkResponse),
            ops.flat_map(lambda i: i.content.directories),
        ).subscribe(TestObserver())

        for f in expected_dirs:
            self.assertIn(os.path.join(self.wordkir, f), actual_dirs)

    def test_walk_file_and_dir(self):

        expected_files = [
            os.path.join('dfoo', 'foo'), 
            os.path.join('dbar', 'bar'),
            os.path.join('dbiz', 'biz'),
        ]
        expected_dirs = ['dfoo', 'dbar', 'dbiz']
        actual_files = []
        create_file_tree(self.wordkir, expected_dirs, expected_files)
        source = walk.make_driver().call(walk.Sink(request=rx.just(
            walk.Walk(top=self.wordkir, id='test', recursive=True)
        )))

        class TestObserver(Observer):
            def on_next(self, i):
                actual_files.append(i)

            def on_completed(self):
                return

            def on_error(self, e):
                raise Exception(e)

        source.response.pipe(
            ops.filter(lambda i: type(i) is walk.WalkResponse),
            ops.flat_map(lambda i: i.content.directories),
            ops.flat_map(lambda i: i.files),
        ).subscribe(TestObserver())

        for f in expected_files:
            self.assertIn(os.path.join(self.wordkir, f), actual_files)
