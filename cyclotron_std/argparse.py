from collections import namedtuple
import argparse as std
import rx
import rx.operators as ops


class ArgumentParser(std.ArgumentParser):
    """ This overloaded ArgumentParser class avoids that the parser exits in
    case of parsing error. This allows to gracefully handle errors.
    """

    def error(self, message):
        raise NameError(message)

# config items
Parser = namedtuple('Parser', ['description'])
ArgumentDef = namedtuple('ArgumentDef', ['name', 'help'])
ArgumentDef.__new__.__defaults__ = ('',)

# output items
Argument = namedtuple('Argument', ['key', 'value'])


def argparse(description, arguments):
    """ A command line argument parser.
    Parses arguments coming from the argv Observable and outputs them as
    Argument items in the output observable.

    Parameters
    -----------
    argv : Observable
        An Observable of strings.
    parser : Observable
        An Observable containing one Parser item.
    arguments : Observable
        An Observable containing ArgumentDef items.


    Returns
    -------
    Observable
        An Observable of Argument items.
    """

    def _argparse(argv):

        parser = ArgumentParser(description=description)
        for arg in arguments:
            parser.add_argument(arg.name, help=arg.help)

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

    return _argparse
