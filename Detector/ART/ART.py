#!/usr/bin/env python
from subprocess import call
class ARTDetector(object):
    ROOT = '/home/wangjing/Dropbox/Research/sadit'
    HOME = ROOT + '/Detector/ART'
    inter_csv_data = HOME + '/output.csv'
    def __init__(self, desc={}):
        self.__dict__.update(desc)

    def compile(self):
        call(['g++', 'ART_anomoly_linux.cpp', '-o', 'ART'])
        call(['g++', 'simple.cpp', '-o', 'parse'])

    def set_args(self, argv):
        pass

    def clean(self):
        call(['rm', 'ART'])
        call(['rm', 'parse'])

    def detect(self, data_handler):
        call([self.HOME + '/parse', '-fs', '-i', data_handler.data.f_name, '-o', self.inter_csv_data])
        call([self.HOME + '/ART', '-i1', self.inter_csv_data])

    def plot(self, pic_show=True, pic_name=None):
        import matplotlib.pyplot as plt
        fid = open(self.HOME + '/anomalyTimeData.txt', 'r')
        ano_t = []
        while True:
            tline = fid.readline()
            if not tline: break
            ano_t.append(float(tline.rsplit()[0]))
        plt.plot(ano_t, [1] * len(ano_t), '+r')
        if pic_name:
            plt.savefig(pic_name)
        if pic_show:
            plt.show()

if __name__ == "__main__":
    art = ARTDetector()
    # art.clean()
    # art.compile()
    art.plot()

