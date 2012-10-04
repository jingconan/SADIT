#!/usr/bin/env python
from Detector import detect
import copy

class Compare(object):
    """
    Compare Different methods and plot the result in
    """
    def __init__(self, desc_opt):
        self.desc_opt = desc_opt
        self.change_opt = get_attr_list(self.desc_opt)
        if self.change_opt:
            self.comb_num = reduce(operator.mul, [len(v) for k, v in self.change_opt.iteritems()])
            self.comb = itertools.product(*self.change_opt.values())
            self.comb_name = list(self.change_opt.keys())

if __name__ == "__main__":
    import search_arg_settings
    import argparse
    parser = argparse.ArgumentParser(description='DetectArgSearch')
    parser.add_argument('--file', dest='flow_file', default=None,
            help = """the flow file used by experiment, if this option
            is set, it will override the settings in setting file""")
    args = parser.parse_args()
    if args.flow_file:
        search_arg_settings.desc['flow_file'] = args.flow_file
    cls = DetectArgSearch(search_arg_settings.desc)
    cls.run()
