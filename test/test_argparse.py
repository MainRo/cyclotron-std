from unittest import TestCase

import reactivex as rx
import reactivex.operators as ops
import cyclotron_std.argparse as argparse


class ArgparseTestCase(TestCase):

    def test_creation(self):
        parser = argparse.ArgumentParser("test_parse")
        parse = argparse.parse(parser)
        self.assertIsNotNone(parse)

    def test_parse(self):
        parser = argparse.ArgumentParser("test_parse")
        parser.add_argument("--foo")

        expected_result = [
            argparse.Argument(key="foo", value="fooz")
        ]

        actual_result = None

        def set_result(i):
            nonlocal actual_result
            actual_result = i

        args = rx.from_(["--foo", "fooz"])
        args.pipe(
            argparse.parse(parser),
            ops.to_list()).subscribe(set_result)
        self.assertEqual(expected_result, actual_result)

    def test_parse_bad_arg(self):
        parser = argparse.ArgumentParser("test_parse")
        parser.add_argument("--foo")

        actual_result = None

        def on_error(error):
            nonlocal actual_result
            actual_result = error

        args = rx.from_(["--bar", "barz"])
        args.pipe(argparse.parse(parser)).subscribe(on_error=on_error)
        self.assertIn("unrecognized arguments", actual_result)
