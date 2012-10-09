import argparse
class BaseDetector(object):
    def set_args(self, argv):
        """set argument and update the desc"""
        parser = argparse.ArgumentParser()
        self.init_parser(parser)
        args = parser.parse_args(argv)
        m_args = dict((k, v) for k, v in args.__dict__.iteritems() if v is not None)
        self.desc.update(m_args)

    def init_parser(self, parser):
        pass

    def detect(self, data_file):
        """detect data_file"""
        pass

class WindowDetector(BaseDetector):
    def init_parser(self, parser):
        parser.add_argument('--interval', default=None, type=float,
                help='interval between two consequent detection')
        parser.add_argument('--win_size', default=None, type=float,
                help='window_size')
        parser.add_argument('--win_type', default=None,
                help="window type 'flow'|'time'")
        parser.add_argument('--max_detect_num', default=None,
                help='max detection number, useful for debug')

        parser.add_argument('--normal_rg', default=None,
                help="""normal range, when it is none, use the whole data as
                the norminal data set""")
