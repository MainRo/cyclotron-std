from unittest import TestCase

import rx
import rx.operators as ops
import cyclotron_std.argparse as argparse


class ArgparseTestCase(TestCase):

    def test_creation(self):
        parse = argparse.argparse("", [])
        self.assertIsNotNone(parse)

    def test_parse(self):
        parse = argparse.argparse(
            "test_parse", [
                argparse.ArgumentDef(name="--foo"),
            ])

        expected_result = [
            argparse.Argument(key="foo", value="fooz")
        ]

        actual_result = None

        def set_result(i):
            nonlocal actual_result
            actual_result = i

        args = rx.from_(["--foo", "fooz"])
        args.pipe(
            parse,
            ops.to_list()).subscribe(set_result)
        self.assertEqual(expected_result, actual_result)

    def test_parse_bad_arg(self):
        parse = argparse.argparse(
            "test_parse", [
                argparse.ArgumentDef(name="--foo"),
            ])

        actual_result = None

        def on_error(error):
            nonlocal actual_result
            actual_result = error

        args = rx.from_(["--bar", "barz"])
        args.pipe(parse).subscribe(on_error=on_error)
        self.assertIn("unrecognized arguments", actual_result)
