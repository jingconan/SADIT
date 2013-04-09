import argparse
import settings
from util import abstract_method

class BaseExper(object):
    ROOT = settings.ROOT
    def __init__(self, argv, parser=None):
        if parser is None:
            parser = argparse.ArgumentParser(add_help=False)
        self.parser = parser
        self.init_parser(parser)
        self.args, self.res_args = parser.parse_known_args(argv)

    def init_parser(self, parser):
        abstract_method()

    def run(self):
        abstract_method()
