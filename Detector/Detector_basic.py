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
import os
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

    @staticmethod
    def find_abnormal_windows(entropy, entropy_threshold=None, ab_win_portion=None, ab_win_num=None):
        """find abnormal windows. There are three standards to select abnormal windows:
            1. when the entropy >= entropy_threshold
            2. when it is winthin the top *portion* of entropy, 0 <= *portion* <= 1
            3. when it is the top *sel_num* of entropy
        the priority of 1 > 2 > 3.
        """
        num = len(entropy)
        abnormal_window_index = []
        if not entropy_threshold:
            if ab_win_portion:
                ab_win_num = int( num * ab_win_portion )
            sorted_entropy = sorted(entropy)
            entropy_threshold = sorted_entropy[-1*ab_win_num]
        return [ i for i in xrange(num) if entropy[i] >= entropy_threshold ]


    def _export_abnorma_flow_entropy(self, entropy, fname,
            entropy_threshold=None, ab_win_portion=None, ab_win_num=None):

        ab_idx = self.find_abnormal_windows(entropy, entropy_threshold, ab_win_portion, ab_win_num)
        rg_type = self.desc['win_type']
        win_size = self.desc['win_size']
        interval = self.desc['interval']
        st = 0
        fid = open(fname, 'w')
        seq = -1
        for idx in ab_idx:
            seq += 1
            st = self.record_data['winT'][idx] if rg_type == 'time' else (interval * idx)
            data, _ = self.data_file.get_fea_slice([st, st+win_size], rg_type)
            sp, ep = self.data_file.data._get_where([st, st+win_size], rg_type)
            fid.write('Seq # [%i] for abnormal window: [%i], entropy: [%f], start time [%f]\n'%(seq, idx, entropy[idx], st))
            i = sp-1
            for l in data:
                i += 1
                data_str = '\t'.join( ['%s - %f'%tuple(v) for v in zip(self.data_file.get_fea_list(), l)] )
                fid.write('Sample # %i\t%s\n'%(i, data_str))

        fid.close()

    def export_abnormal_flow(self, fname, entropy_threshold=None, ab_win_portion=None, ab_win_num=None):
        """
        export the abnormal flows for abnormal windows
        """
        mf, mb = zip(*self.record_data['entropy'])
        # select portion of the window to be abnormal
        dirname = os.path.dirname(fname)
        basename = os.path.basename(fname)

        # for model free entropy
        self._export_abnorma_flow_entropy(mf, dirname + '/mf-' + basename, entropy_threshold, ab_win_portion, ab_win_num)

        # for model based entropy
        self._export_abnorma_flow_entropy(mb, dirname + '/mb-' + basename, entropy_threshold, ab_win_portion, ab_win_num)

