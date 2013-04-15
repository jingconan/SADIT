import argparse
import settings
import copy
# from util import abstract_method, load_para, Namespace
from util import abstract_method
from util import load_para
from util import update_not_none

class BaseExper(object):
    ROOT = settings.ROOT
    def __init__(self, argv, parser=None):
        # import ipdb;ipdb.set_trace()
        if parser is None:
            parser = argparse.ArgumentParser(add_help=False)
        self.parser = parser
        self.init_parser(parser)
        self.args, self.res_args = parser.parse_known_args(argv)

        if self.args.config is None:
            print('You must specifiy --config option, run with -h option to see help')
            import sys; sys.exit(0)
        self.desc = copy.deepcopy(self.args.config['DETECTOR_DESC'])
        update_not_none(self.desc, self.args.__dict__)

    def init_parser(self, parser):
        parser.add_argument('-c', '--config', default=None,
                # type=lambda x: load_para(x, Namespace),
                type=lambda x: load_para(x),
                help="""config""")

    def run(self):
        abstract_method()
