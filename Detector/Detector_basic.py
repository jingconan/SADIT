#!/usr/bin/env python
"""
This file contains all the detection techniques
"""
__author__ = "Jing Conan Wang"
__email__ = "wangjing@bu.edu"
__status__ = "Development"

import sys
sys.path.append("..")
# import settings
try:
    from matplotlib.pyplot import figure, plot, show, subplot, title, savefig
    VIS = True
except:
    print 'no matplotlib'
    VIS = False

from DetectorLib import I1, I2
from util import DataEndException, FetchNoDataException,  abstract_method

import cPickle as pickle
# from AnoType import ModelFreeAnoTypeTest, ModelBaseAnoTypeTest
# from DataFile import DataFile, HardDiskFileHandler

class AnoDetector (object):
    """It is an Abstract Base Class for the anomaly detector."""
    def __init__(self, desc):
        self.desc = desc
        # self.record_data = dict(IF=[], IB=[], winT=[], threshold=[], em=[])
        self.record_data = dict(entropy=[], winT=[], threshold=[], em=[])

    def __call__(self, *args, **kwargs):
        return self.detect(*args, **kwargs)

    def get_em(self, rg, rg_type):
        """abstract method. Get empirical measure,
        rg is a list specify the start and the end point of the data
            that will be used
        rg_type is the type of the rg, can be ['flow'|'time']"""
        abstract_method()

    def I(self, em1, em2):
        """abstract method to calculate the difference of two
        empirical measure"""
        abstract_method()

    def record(self, **kwargs):
        for k, v in kwargs.iteritems():
            self.record_data[k].append(v)

    def reset_record(self):
        for k, v in self.record_data.iteritems():
            self.record_data[k] = []

    # def detect(self, data_file, nominal_rg = [0, 1000], rg_type='time',  max_detect_num=None):
    def detect(self, data_file):
        """main function to detect. it will slide the window, get the emperical
        measure and get the indicator"""
        nominal_rg = self.desc['normal_rg']
        rg_type = self.desc['win_type']
        max_detect_num = self.desc['max_detect_num']

        self.data_file = data_file
        self.norm_em = self.get_em(rg=nominal_rg, rg_type=rg_type)

        win_size = self.desc['win_size']
        interval = self.desc['interval']
        time = self.desc['fr_win_size'] if ('flow_rate' in self.desc['fea_option'].keys()) else 0

        i = 0
        while True:
            i += 1
            if max_detect_num and i > max_detect_num:
                break
            if rg_type == 'time' : print 'time: %f' %(time)
            else: print 'flow: %s' %(time)

            try:
                # d_pmf, d_Pmb, d_mpmb = self.data_file.get_em(rg=[time, time+win_size], rg_type='time')
                em = self.get_em(rg=[time, time+win_size], rg_type=rg_type)
                entropy = self.I(em, self.norm_em)
                self.record( entropy=entropy, winT = time, threshold = 0, em=em )
            except FetchNoDataException:
                print 'there is no data to detect in this window'
            except DataEndException:
                print 'reach data end, break'
                break

            time += interval

        return self.record_data

    def plot_entropy(self, pic_show=True, pic_name=None):
        if not VIS: return
        rt = self.record_data['winT']
        figure()
        plot(rt, self.record_data['entropy'])

        if pic_name: savefig(pic_name)
        if pic_show: show()

    def dump(self, data_name):
        pickle.dump( self.record_data, open(data_name, 'w') )

class ModelFreeAnoDetector(AnoDetector):
    def I(self, d_pmf, pmf):
        return I1(d_pmf, pmf)

    def get_em(self, rg, rg_type):
        """get empirical measure"""
        pmf, Pmb, mpmb = self.data_file.get_em(rg, rg_type)
        return pmf, Pmb, mpmb

class ModelBaseAnoDetector(AnoDetector):
    def I(self, em, norm_em):
        d_Pmb, d_mpmb = em
        Pmb, mpmb = norm_em
        return I2(d_Pmb, d_mpmb, Pmb, mpmb)

    def get_em(self, rg, rg_type):
        pmf, Pmb, mpmb = self.data_file.get_em(rg, rg_type)
        return Pmb, mpmb

class FBAnoDetector(AnoDetector):
    """model free and model based together"""
    def I(self, em, norm_em):
        d_pmf, d_Pmb, d_mpmb = em
        pmf, Pmb, mpmb = norm_em
        return I1(d_pmf, pmf), I2(d_Pmb, d_mpmb, Pmb, mpmb)

    def get_em(self, rg, rg_type):
        """get empirical measure"""
        pmf, Pmb, mpmb = self.data_file.get_em(rg, rg_type)
        return pmf, Pmb, mpmb

    def _save_gnuplot_file(self):
        res_f_name = './res.dat'
        fid = open(res_f_name, 'w')
        rt = self.record_data['winT']
        mf, mb = zip(*self.record_data['entropy'])
        for i in xrange(len(rt)):
            fid.write("%f %f %f\n"%(rt[i], mf[i], mb[i]))
        fid.close()

    def plot_entropy(self, pic_show=True, pic_name=None):
        if not VIS: self._save_gnuplot_file(); return;

        rt = self.record_data['winT']
        figure()
        subplot(211)
        mf, mb = zip(*self.record_data['entropy'])
        plot(rt, mf)
        title('model free')
        subplot(212)
        plot(rt, mb)
        title('model based')

        if pic_name: savefig(pic_name)
        if pic_show: show()

    def find_abnormal_windows():
        """find abnormal windows"""
        pass

    def export_abnormal_flow(self, fname, portion=0.1):
        """
        export the abnormal flows for abnormal windows
        """
        mf, mb = zip(*self.record_data['entropy'])
        # select portion of the window to be abnormal
        win_num = len(mf)
        sel_num = int( win_num * portion )

        pass
