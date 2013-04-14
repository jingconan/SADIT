import argparse
import settings
from util import abstract_method, load_para, Namespace

class BaseExper(object):
    ROOT = settings.ROOT
    def __init__(self, argv, parser=None):
        # import ipdb;ipdb.set_trace()
        if parser is None:
            parser = argparse.ArgumentParser(add_help=False)
        self.parser = parser
        self.init_parser(parser)
        self.args, self.res_args = parser.parse_known_args(argv)

    def init_parser(self, parser):
        parser.add_argument('-c', '--config', default=None,
                # type=lambda x: load_para(x, Namespace),
                type=lambda x: load_para(x),
                help="""config""")

    def run(self):
        abstract_method()
