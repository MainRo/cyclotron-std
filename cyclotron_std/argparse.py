from collections import namedtuple
import argparse as std

from rx import AnonymousObservable

class ArgumentParser(std.ArgumentParser):
    """ This overloaded ArgumentParser class avoids that the parser exits in
    case of parsing error. This allows to gracefully handle errors.
    """

    def error(self, message):
        raise NameError(message)

# config items
Parser = namedtuple('Parser', ['description'])
AddArgument = namedtuple('AddArgument', ['name', 'help'])
AddArgument.__new__.__defaults__ = ('',)

# output items
Argument = namedtuple('Argument', ['key', 'value'])

def argparse(parser, add_argument, argv):
    """ Parses arguments coming from the argv Observable and outputs them as
    Argument items in the output observable.

    Arguments:
    Parser -- An Observable containing one Parser item.
    add_argument -- An Observable containing AddArgument items.
    argv -- An Observable of strings.

    Returns an Observable of Argument items.
    """
    def add_arg(parser, arg_spec):
        parser.add_argument(arg_spec.name, help=arg_spec.help)
        return parser


    parse_request = parser \
        .map(lambda i: ArgumentParser(description=i.description)) \
        .combine_latest(add_argument, lambda parser, arg_spec: add_arg(parser,arg_spec)) \
        .last() \
        .combine_latest(argv.to_list(), lambda parser, args: (parser,args))

    def subscribe(observer):
        def on_next(value):
            parser, args = value
            try:
                args = parser.parse_args(args)
                for key,value in vars(args).items():
                    observer.on_next(Argument(key=key, value=value))
            except NameError as exc:
                observer.on_error("{}\n{}".format(exc, parser.format_help()))

        return parse_request.subscribe(on_next, observer.on_error, observer.on_completed)

    return AnonymousObservable(subscribe)
