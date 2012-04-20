#!/usr/bin/env python
import sys
sys.path.append("..")
import settings
from DetectorLib import I1, I2
from util import DataEndException
from matplotlib.pyplot import figure, plot, show, subplot, title
import cPickle as pickle
# from AnoType import ModelFreeAnoTypeTest, ModelBaseAnoTypeTest
from Detector.DataFile import DataFile

class AnoDetector (object):
    def __init__(self, desc):
        self.desc = desc
        # self.record_data = dict(IF=[], IB=[], winT=[], threshold=[], em=[])
        self.record_data = dict(entropy=[], winT=[], threshold=[], em=[])

    def __call__(self, *args, **kwargs):
        return self.detect(*args, **kwargs)

    def record(self, **kwargs):
        for k, v in kwargs.iteritems():
            self.record_data[k].append(v)

    def reset_record(self):
        for k, v in self.record_data.iteritems():
            self.record_data[k] = []

    def detect(self, data_file):
        self.data_file = data_file
        self.norm_em = self.get_em(rg=[0, 1000], rg_type='time')

        win_size = self.desc['win_size']
        interval = self.desc['interval']
        time = self.desc['fr_win_size']

        while True:
            print 'time: %f' %(time)
            try:
                # d_pmf, d_Pmb, d_mpmb = self.data_file.get_em(rg=[time, time+win_size], rg_type='time')
                em = self.get_em(rg=[time, time+win_size], rg_type='time')
                entropy = self.I(em, self.norm_em)
                self.record( entropy=entropy, winT = time, threshold = 0, em=em )
                time += interval
            except DataEndException:
                print 'reach data end, break'
                break
        return self.record_data

    def plot_entropy(self):
        rt = self.record_data['winT']
        figure()
        plot(rt, self.record_data['entropy'])
        show()

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
        """get empirical measure"""
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

    def plot_entropy(self):
        rt = self.record_data['winT']
        figure()
        subplot(211)
        mf, mb = zip(*self.record_data['entropy'])
        plot(rt, mf)
        title('model free')
        subplot(212)
        plot(rt, mb)
        title('model based')
        show()


def detect(f_name, win_size, fea_option, detector_type):
    detector_map = {
            'mf':ModelFreeAnoDetector,
            'mb':ModelBaseAnoDetector,
            'mfmb':FBAnoDetector,
            }
    # data_file = Detector.DataFile.DataFile(f_name,
                # settings.DETECTOR_DESC['win_size'],
                # settings.DETECTOR_DESC['fea_list'])
    data_file = DataFile(f_name, win_size, fea_option)
    # detect = ModelFreeAnoDetector(settings.DETECTOR_DESC)
    detector = detector_map[detector_type](settings.DETECTOR_DESC)
    detector(data_file)
    detector.plot_entropy()

    # type_detector = ModelFreeAnoTypeTest(detect, 3000, settings.ANO_DESC['T'])
    # type_detector.detect_ano_type()

    # type_detector = ModelBaseAnoTypeTest(detect, 3000, settings.ANO_DESC['T'])
    # type_detector.detect_ano_type()

    # import pdb;pdb.set_trace()
    # detect.plot_entropy()

if __name__ == "__main__":
    import sys
    print 'sys.argv, ', sys.argv
    # compare(sys.argv[1])

    # import pdb;pdb.set_trace()
    # detect.plot_entropy()
