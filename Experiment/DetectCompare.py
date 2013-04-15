#!/usr/bin/env python
""" Compare different method and plot the temporal
results in the same window.
"""
from __future__ import print_function, division, absolute_import
from .Detect import Detect
# import copy
import os
import matplotlib.pyplot as plt
from Detector import detector_plot_dump
import cPickle as pickle

class DetectCompare(Detect):
    """ Compare Different methods and plot the result in
    """
    def __init__(self, *args, **kwargs):
        # Detect.__init__(self, *args, **kwargs)
        super(DetectCompare, self).__init__(*args, **kwargs)

    def init_parser(self, parser):
        super(DetectCompare, self).init_parser(parser)
        parser.add_argument('-p', '--comp_methods', default=None, type=lambda x:x.split(','),
                help="""method list that will be compared""")

        parser.add_argument('-f','--dump_folder', default=self.ROOT+'/Share/',
                help="""folder that will store the dump file for each detector""")

        # parser.add_argument('--plot_dump', default=None,
                # help="""plot folder that store the dump several""")

        parser.add_argument('--plot_dump', default=False, action='store_true',
                help="""flag of whether plot_dump""")

    def run(self):
        # res_args = self.res_args

        # if self.args.plot_dump:
        if self.desc['plot_dump']:
            # self.plot_dump(self.args.plot_dump)
            self.plot_dump(self.args.dump_folder)
            return

        d = os.path.abspath(self.args.dump_folder)
        if not os.path.exists(d):
            os.makedirs(d)

        # for method in self.args.comp_methods:
        for method in self.desc['comp_methods']:
            print('method: ', method)
            self.desc['method'] = method
            detector = self.detect()
            print('detector type, ', type(detector))
            detector.dump(self.desc['dump_folder'] + '/dump_' + method + '.txt')

        with open(self.desc['dump_folder '] + '/dump_method_list.txt', 'w') as f:
            pickle.dump(self.desc['comp_methods'], f)


    def plot_dump(self, dump_folder):
        if self.desc.get('comp_methods'):
            method_list = self.desc.get('comp_methods')
        else:
            method_list = pickle.load(open(dump_folder + '/dump_method_list.txt', 'r'))

        fig = plt.figure()
        sp = len(method_list) * 100
        double_fig_methods = ['mfmb', 'robust']
        for m in double_fig_methods:
            if m in method_list:
                sp += 100
        sp += 10

        for method in method_list:
            print('method', method)
            data_name = dump_folder + '/dump_' + method + '.txt'

            if method in double_fig_methods:
                # detector.plot(figure_=fig, subplot_=[sp+1, sp+2],
                        # title_=['mf', 'mb'])
                detector_plot_dump(data_name, method, dict(win_type='time'),
                        figure_=fig, subplot_=[sp+1, sp+2],
                        title_=['mf', 'mb'])
                sp += 2
            else:
                detector_plot_dump(data_name, method, dict(win_type='time'),
                        figure_=fig, subplot_=sp+1,
                        title_=method)
                # detector.plot(figure_=fig, subplot_=sp+1, title_=method)
                sp += 1

        if self.desc.get('pic_name'):
            plt.savefig(self.desc.get('pic_name'))
        if self.desc.get('pic_show'):
            plt.show()
