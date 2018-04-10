from collections import namedtuple
import argparse as std

from rx import Observable

# config items
Parser = namedtuple('Parser', ['description'])
AddArgument = namedtuple('AddArgument', ['name', 'help'])
AddArgument.__new__.__defaults__ = ('',)

# output items
Argument = namedtuple('Argument', ['key', 'value'])

def argparse(parser, add_argument, argv):
    """ Parses arguments coming from the argv Observable and outputs them as
    ParsedArgument items in the output observable.

    Arguments:
    config -- An Observable the must contain one Config item and some Argument
        items.
    argv -- An Observable of strings.

    Returns an Observable of ParsedArgument items.
    """

    def arg_config_accumulator(acc, i):
        if acc is None:
            print("init acc")
            acc = i
        else:
            print("i: {}".format(i))
            acc.add_argument(i.name, help=i.help)
        return acc

    args = argv \
        .scan(lambda acc,i: acc + [i], []) \
        .last()

    parsed_args = parser \
        .map(lambda i: std.ArgumentParser(description=i.description)) \
        .concat(add_argument) \
        .do_action(lambda i: print("concat: {}".format(i))) \
        .scan(arg_config_accumulator, None) \
        .last() \
        .do_action(lambda i: print("done")) \
        .combine_latest(args, lambda parser, args: parser.parse_args(args)) \
        .flat_map(lambda i: Observable.from_(
            [ Argument(key=key, value=value) for key,value in vars(i).items()]))

    return parsed_args
