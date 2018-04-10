from unittest import TestCase

from rx import Observable
import cyclotron_std.argparse as argparse


class ArgparseTestCase(TestCase):

    def test_creation(self):
        args = argparse.argparse(
            Observable.empty(),
            Observable.empty(),
            Observable.empty())

        self.assertIsNotNone(args)

    def test_parse(self):
        args = argparse.argparse(
            Observable.just(argparse.Parser(description="test_parse")),
            Observable.from_([
                argparse.AddArgument(name="--foo"),
            ]),
            Observable.from_(["--foo", "fooz"]))

        expected_result = [
            argparse.Argument(key="foo", value="fooz")
        ]

        actual_result = None
        def set_result(i):
            nonlocal actual_result
            actual_result = i
        args.to_list().subscribe(set_result)
        self.assertEqual(expected_result, actual_result)
