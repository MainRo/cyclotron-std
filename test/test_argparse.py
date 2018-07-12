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
            Observable.from_(["--foo", "fooz"]),
            Observable.just(argparse.Parser(description="test_parse")),
            Observable.from_([
                argparse.ArgumentDef(name="--foo"),
            ]))

        expected_result = [
            argparse.Argument(key="foo", value="fooz")
        ]

        actual_result = None
        def set_result(i):
            nonlocal actual_result
            actual_result = i
        args.to_list().subscribe(set_result)
        self.assertEqual(expected_result, actual_result)

    def test_parse_bad_arg(self):
        args = argparse.argparse(
            Observable.from_(["--bar", "barz"]),
            Observable.just(argparse.Parser(description="test_parse")),
            Observable.from_([
                argparse.ArgumentDef(name="--foo"),
            ]))

        actual_result = None
        def on_error(error):
            nonlocal actual_result
            actual_result = error

        args.subscribe(on_error=on_error)
        self.assertIn("unrecognized arguments", actual_result)
