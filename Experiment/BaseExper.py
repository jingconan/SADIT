import argparse
from sadit import settings
from sadit.util import abstract_method, load_para

class BaseExper(object):
    ROOT = settings.ROOT
    def __init__(self, argv, parser=None):
        # import ipdb;ipdb.set_trace()
        if parser is None:
            parser = argparse.ArgumentParser(add_help=False)
            # parser = argparse.ArgumentParser()
        self.parser = parser
        self.init_parser(parser)
        self.args, self.res_args = parser.parse_known_args(argv)

        if self.args.help:
            self.print_help()
            import sys; sys.exit(0)

        if self.args.config is None:
            print('You must specifiy --config option, run with -h option to see help')
            import sys; sys.exit(0)

    def print_help(self):
        self.parser.print_help()

    def init_parser(self, parser):
        parser.add_argument('-h', '--help', default=False, action='store_true',
                help="""print help message""")
        parser.add_argument('-c', '--config', default=None,
                # type=lambda x: load_para(x, Namespace),
                type=lambda x: load_para(x),
                help="""config""")

    def run(self):
        abstract_method()
