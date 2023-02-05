from collections import namedtuple
import argparse as std
import reactivex as rx
import reactivex.operators as ops


class ArgumentParser(std.ArgumentParser):
    """ This overloaded ArgumentParser class avoids that the parser exits in
    case of parsing error. This allows to gracefully handle errors.
    """

    def error(self, message):
        raise NameError(message)


# output items
Argument = namedtuple('Argument', ['key', 'value'])


def parse(parser):
    """ A command line argument parser.
    Parses arguments coming from the argv Observable and outputs them as
    Argument items in the output observable.

    Parameters
    -----------
    parser : ArgumentParser
        A parser object.

    Returns
    -------
    Function
        A parser function accepting argv as input and returning parsed arguments
    """

    def _parse(argv):
        def subscribe(observer, scheduler):
            def on_next(value):
                try:
                    args = parser.parse_args(value)
                    for key, value in vars(args).items():
                        observer.on_next(Argument(key=key, value=value))
                except NameError as exc:
                    observer.on_error("{}\n{}".format(exc, parser.format_help()))

            return argv.pipe(ops.to_list()).subscribe(
                on_next=on_next,
                on_error=observer.on_error,
                on_completed=observer.on_completed)

        return rx.create(subscribe)

    return _parse
