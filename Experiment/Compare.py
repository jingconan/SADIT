#!/usr/bin/env python
from __future__ import print_function, division
from DetectExper import DetectExper
import copy
import os
import matplotlib.pyplot as plt
from Detector import detector_plot_dump
import cPickle as pickle
class Compare(DetectExper):
    """ Compare Different methods and plot the result in
    """
    def __init__(self, *args, **kwargs):
        DetectExper.__init__(self, *args, **kwargs)
        self.detectors = []

    def init_parser(self, parser):
        super(Compare, self).init_parser(parser)
        parser.add_argument('--comp_methods', default=None, type=lambda x:x.split(','),
                help="""method list that will be compared""")

        parser.add_argument('--dump_folder', default=self.ROOT+'/Share/',
                help="""folder that will store the dump file for each detector""")

        # parser.add_argument('--plot_dump', default=None,
                # help="""plot folder that store the dump several""")

        parser.add_argument('--plot_dump', default=False, action='store_true',
                help="""flag of whether plot_dump""")

    def run(self):
        if self.args.plot_dump:
            # self.plot_dump(self.args.plot_dump)
            self.plot_dump(self.args.dump_folder)
            return

        fig = plt.figure()
        sp = len(self.args.comp_methods) * 100
        sp += 10

        d = os.path.abspath(self.args.dump_folder)
        if not os.path.exists(d):
            os.makedirs(d)

        for method in self.args.comp_methods:
            print('method: ', method)
            self.args.method = method
            detector = self.detect()
            print('detector type, ', type(detector))
            self.detectors.append(copy.deepcopy(detector))

            if method == 'mfmb':
                detector.plot(figure_=fig, subplot_=[sp+1, sp+2],
                        title_=['mf', 'mb'])
                sp += 2
            else:
                detector.plot(figure_=fig, subplot_=sp+1, title_=method)
                # detector.plot(figure_=fig, subplot_=sp+1, ylabel_=method)
                sp += 1
            detector.dump(self.args.dump_folder + '/dump_' + method + '.txt')

        pickle.dump(self.args.comp_methods, open(self.args.dump_folder + '/dump_method_list.txt', 'w'))

        if self.args.pic_name:
            plt.savefig(self.args.pic_name)
        if self.args.pic_show:
            plt.show()

    def plot_dump(self, dump_folder):
        if self.args.comp_methods:
            method_list = self.args.comp_methods
        else:
            method_list = pickle.load(open(dump_folder + '/dump_method_list.txt', 'r'))
        fig = plt.figure()
        sp = len(method_list) * 100
        sp += 10

        for method in method_list:
            data_name = dump_folder + '/dump_' + method + '.txt'

            if method == 'mfmb':
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

        if self.args.pic_name:
            plt.savefig(self.args.pic_name)
        if self.args.pic_show:
            plt.show()


