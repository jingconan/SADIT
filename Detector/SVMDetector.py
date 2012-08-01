"""
This file is the flow by flow svm detector
"""
import settings
SVM_FOLDER = settings.ROOT + '/tools/libsvm-3.12'
import subprocess

def write_svm_data_file(label, fea, f_name):
    fid = open(f_name, 'w')
    assert(len(label) == len(fea))
    n = len(label)
    for i in xrange(n):
        fea_v = fea[i]
        line = ['%s:%s'%(j+1, fea_v[j]) for j in xrange(len(fea_v)) ]
        fid.write(str(label[i]) + ' ' + ' '.join(line) + '\n')

from Detector.DataHandler import HardDiskFileHandler
class SVMDataHandler(HardDiskFileHandler):
    """Data Hanlder for SVM approach. It use a set of features
    which will be defined here"""
    pass

class SVMDetector(object):
    """base class for SVM Detector"""
    def __init__(self, desc):
        self._defaults()
        self.__dict__.update(desc)

    def _defaults(self):
        """default value for SVM detector parameters"""
        self.svm_dat_file= settings.ROOT + '/Share/test.dat'
        self.svm_model_file= settings.ROOT + '/Share/test.model'
        self.svm_pred_file= settings.ROOT + '/Share/test.pred'

        self.scale_para_file = settings.ROOT + '/Share/scale.sf'

    def scale(self):
        print 'start to scale ...'
        scale_file = self.svm_dat_file + '.scale'
        subprocess.check_call(' '.join([SVM_FOLDER + '/svm-scale',
            '-s', self.scale_para_file,
            self.svm_dat_file,
            '>',
            scale_file
            ]), shell=True)
        self.svm_dat_file = scale_file

    def train(self):
        print 'start to train...'
        subprocess.check_call([SVM_FOLDER + '/svm-train',
            '-s', '2',
            '-n', '0.001',
            '-g', str(self.gamma),
            self.svm_dat_file,
            self.svm_model_file])

    def predict(self):
        print 'start to predict...'
        subprocess.check_call([SVM_FOLDER + '/svm-predict',
            self.svm_dat_file,
            self.svm_model_file,
            self.svm_pred_file])

    def load_pred(self):
        fid = open(self.svm_pred_file)
        self.pred = []
        while True:
            line = fid.readline()
            if not line: break
            self.pred.append(int(line))
        fid.close()

    def stat(self):
        pred_num = dict()
        for val in [-1, 1]:
            num = len([val for p in self.pred if p == val])
            pred_num[val] = num
        self.ano_val = 1 if pred_num[1] < pred_num[-1] else -1
        print 'total flows', len(self.pred), 'alarm num, ', pred_num[self.ano_val]


class SVMFlowByFlowDetector(SVMDetector):
    """SVM Flow By Flow Anomaly Detector Method"""

    def write_dat(self, data):
        fea = data.get_fea_slice()
        # fea_str = data.data.get_fea_slice(['flow_size'])
        # fea = [[float(s[0])] for s in fea_str]
        # import pdb;pdb.set_trace()
        label = [0] * len(fea)
        write_svm_data_file(label, fea, self.svm_dat_file)


    def detect(self, data):
        self.data_file = data
        self.write_dat(data)
        self.scale()
        self.train()
        self.predict()
        self.load_pred()

    def plot_pred(self, pic_show=True, pic_name=None):
        import matplotlib.pyplot as plt
        self.stat()
        fea_slice = self.data_file.data.get_fea_slice(fea=['start_time'])
        min_t = float(fea_slice[0][0])
        start_time = [float(v[0])-min_t for v in fea_slice]
        x = [start_time[i] for i in xrange(len(start_time)) if self.pred[i] == self.ano_val]
        y = [1 for i in xrange(len(start_time)) if self.pred[i] == self.ano_val]
        # plt.plot(start_time, self.pred, '+')
        plt.plot(x, y, '+')
        if pic_show: plt.show()
        if pic_name: plt.savefig(pic_name)

from collections import Counter
from util import DataEndException, FetchNoDataException
from DataHandler import PreloadHardDiskFile
class SVMTemporalHandler(object):
    """Data Hanlder for SVM Temporal Detector approach. It use a set of features
    which will be defined here"""
    handler = {
            'src_ip': lambda x:[v[0] for v in x],
            'start_time': lambda x: [float(v[0]) for v in x],
            'flow_size': lambda x: [float(v[0]) for v in x],
            }

    def __init__(self, fname):
        self._init_data(fname)
        self.update_unique_src_ip()
        self.large_flow_thres = 5e5

    def update_unique_src_ip(self):
        """be carefule to update unique src ip when using a new file"""
        self.unique_src_ip = list(set(self.get('src_ip')))

    def _init_data(self, f_name):
        self.data = PreloadHardDiskFile(f_name)

    def get(self, fea, rg=None, rg_type=None):
        """receive feature name as input"""
        raw = self.data.get_fea_slice([fea], rg, rg_type)
        return self.handler[fea](raw)

    def get_svm_feature(self, rg=None, rg_type=None):
        """ suppose m is the number of unique source ip address in this data.
        the feature is 2mx1,
        - the first m feature is the frequency of flows with
        each source ip address,
        - the second m feature is the frequence of larges
        flows whose size is > self.large_flow_thres with each source ip address"""
        src_ip = self.get('src_ip', rg, rg_type)
        flow_size = self.get('flow_size', rg, rg_type)
        n = len(src_ip)
        ct = Counter(src_ip)
        fea_total_flow = [ct[ip] for ip in self.unique_src_ip]

        # import pdb;pdb.set_trace()
        lf_src_ip = [src_ip[i] for i in xrange(n) if flow_size[i] > self.large_flow_thres]
        ct = Counter(lf_src_ip)
        fea_large_flow = [ct[ip] for ip in self.unique_src_ip]
        return fea_total_flow + fea_large_flow

class SVMTemporalDetector(SVMDetector):
    """SVM Temporal Difference Detector. Proposed by R.L Taylor. Implemented by
    J. C. Wang <wangjing@bu.ed> """
    def write_dat(self, data_handler):
        """construct feature and write dat data for libsvm use. data is a Data Handler Class. refer
        DataHandler.py for details.
        """
        fea_list = []
        time = 0
        i = 0
        while True:
            i += 1
            if self.max_detect_num and i > self.max_detect_num:
                break
            if self.rg_type == 'time' : print 'time: %f' %(time)
            else: print 'flow: %s' %(time)

            try:
                fea = data_handler.get_svm_feature(rg=[time, time+self.win_size], rg_type=self.rg_type)
                fea_list.append(fea)
            except FetchNoDataException:
                print 'there is no data to detect in this window'
            except DataEndException:
                print 'reach data end, break'
                break

            time += self.interval

        self.detect_num = i - 1

        label = [0] * len(fea_list)
        write_svm_data_file(label, fea_list, self.svm_dat_file)

    def detect(self, data_handler):
        self.write_dat(data_handler)
        self.train()
        self.scale()
        self.train()
        self.predict()
        self.load_pred()

    def plot_pred(self, pic_show=True, pic_name=None):
        import matplotlib.pyplot as plt
        self.stat()
        ano_idx = [i for i in xrange(self.detect_num) if self.pred[i] == self.ano_val]
        x = [i*self.interval for i in ano_idx]
        y = [self.pred[i] for i in ano_idx]
        plt.plot(x, y, '+')
        if pic_show: plt.show()
        if pic_name: plt.savefig(pic_name)



if __name__ == "__main__":
    desc = dict(gamma=0.1,
            svm_dat_file='./test.dat',
            svm_model_file='./test.model',
            svm_pred_file='./test.pred')
    detector = SVMFlowByFlowDetector(desc)
    detector.detect()
