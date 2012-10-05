"""
This file is the flow by flow svm detector
"""
import settings
SVM_FOLDER = settings.ROOT + '/tools/libsvm-3.12'
import subprocess
try:
    import matplotlib.pyplot as plt
except:
    plt = False
from mod_util import plot_points
import cPickle as pickle

def write_svm_data_file(label, fea, f_name):
    fid = open(f_name, 'w')
    assert(len(label) == len(fea))
    n = len(label)
    for i in xrange(n):
        fea_v = fea[i]
        line = ['%s:%s'%(j+1, fea_v[j]) for j in xrange(len(fea_v)) ]
        fid.write(str(label[i]) + ' ' + ' '.join(line) + '\n')

# from Detector.DataHandler import HardDiskFileHandler
# from Detector.DataHandler import QuantizeDataHandler
# class SVMDataHandler(HardDiskFileHandler):
# class SVMDataHandler(QuantizeDataHandler):
#     """Data Hanlder for SVM approach. It use a set of features
#     which will be defined here"""
#     pass

import argparse
class SVMDetector(object):
    """base class for SVM Detector"""
    def __init__(self, desc):
        self.__dict__.update(desc)

    @property
    def rg_type(self): return self.win_type

    def init_parser(self, parser):
        parser.add_argument('--svm_type', default=0,
                help="""
-s svm_type : set type of SVM (default 0)
    0 -- C-SVC
    1 -- nu-SVC
    2 -- one-class SVM
    3 -- epsilon-SVR
    4 -- nu-SVR
                """)
        parser.add_argument('--kernel_type', default='2',
                help = """
    0 -- linear: u'*v
    1 -- polynomial: (gamma*u'*v + coef0)^degree
    2 -- radial basis function: exp(-gamma*|u-v|^2)
    3 -- sigmoid: tanh(gamma*u'*v + coef0)
                """)

        parser.add_argument('--pca_var_pic', default=None,
                help = "the picture name for pca component variable",
                )
        parser.add_argument('--pca_th', default=0.9, type=float,
                help = "the threshold for pca",
                )

        parser.add_argument('--gamma', default='0.01',
                help="set gamma in kernel function")
        parser.add_argument('--nu', default='0.01',
                help="set the parameter nu of nu-SVM, one-class SVM and nu-SVR")
        parser.add_argument('--degree', default=3, type=int,
                help="degreee for polynomial kernel")
        parser.add_argument('--svm_dat_file', default= settings.ROOT + '/Share/test.dat',
                help = "svm data file path")
        parser.add_argument('--svm_model_file', default = settings.ROOT + '/Share/test.model',
                help = "svm model file path")
        parser.add_argument('--svm_pred_file', default=settings.ROOT + '/Share/test.pred',
                help="svm predict file path")
        parser.add_argument('--scale_para_file', default=settings.ROOT + '/Share/scale.sf',
                help="svm")

    def set_args(self, argv):
        parser = argparse.ArgumentParser(description='SVMDetector')
        self.init_parser(parser)
        self.args = parser.parse_args(argv)
        self.__dict__.update(self.args.__dict__)

    @staticmethod
    def norm_fea(fea):
        """normalize the feature to [0, 1]"""
        zip_fea = zip(*fea)
        new_zip_fea = []
        for zf in zip_fea:
            max_val = max(zf)
            min_val = min(zf)
            rg = max_val - min_val
            if rg == 0:
                new_zip_fea.append(zf)
                continue
            # print 'max_val, ', max_val
            # print 'min_val, ', min_val
            # import pdb;pdb.set_trace()
            new_zip_fea.append([(f - min_val) * 1.0 /rg for f in zf])
        return zip(*new_zip_fea)

    def pca(self, fea_list):
        if not NUMPY:
            return fea_list

        pc = PCA(fea_list, self.pca_th)

        if self.pca_var_pic:
            from matplotlib import pyplot as plt
            plt.plot(pc.d, 'b-+')
            plt.title('variance of each component at pca')
            plt.savefig(self.pca_var_pic)
            plt.clf()
        # return np.dot(np.dot( pc.U[:, 0:pc.npc],  np.diag(pc.d[0:pc.npc]) ), pc.Vt[0:pc.npc, :])
        return np.dot( np.array(fea_list), pc.Vt[0:pc.npc, :].T)


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
            '-t', str(self.kernel_type),
            '-d', str(self.degree),
            '-n', str(self.nu),
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

    def plot(self, *args, **kwargs):
        self.stat()
        self.plot_pred(*args, **kwargs)

    def plot_dump(self, data_name, *args, **kwargs):
        """load the dumped results and plot it
        """
        data = pickle.load(open(data_name, 'r'))
        self.__dict__.update(data)
        self.plot_pred(*args, **kwargs)

    def get_start_time(self):
        return self.data_file.data.get_fea_slice(fea=['start_time'])

    def dump(self, data_name):
        pickle.dump( dict(pred=self.pred, ano_val=self.ano_val), open(data_name, 'w') )

class SVMFlowByFlowDetector(SVMDetector):
    """SVM Flow By Flow Anomaly Detector Method"""
    # MAX_FLOW_ONE_TIME = 1e4 # max number of flow it will compare each time

    def init_parser(self, parser):
        super(SVMFlowByFlowDetector, self).init_parser(parser)
        parser.add_argument('--sample_ratio', default=0.1, type=float,
                help="sample the flows to reduce computation cost, sample ratio of the flows")

    @staticmethod
    def sample(fea, ratio):
        flow_num = len(fea)
        sample_num = int(ratio * flow_num)
        interval = int(flow_num / sample_num)
        sample_fea = [fea[i] for i in xrange(0, flow_num, interval)]
        return sample_fea

    def get_start_time(self):
        start_time = self.data_file.data.get_fea_slice(fea=['start_time'])
        return self.sample(start_time, self.sample_ratio)

    def write_dat(self, data):
        fea = data.get_fea_slice()
        fea = [f[1:] for f in fea] # ignore cluster label
        # import pdb;pdb.set_trace()
        # zip_fea = data.quantize_fea()
        # fea = zip(*zip_fea)
        # fea_str = data.data.get_fea_slice(['flow_size'])
        # fea = [[float(s[0])] for s in fea_str]
        # import pdb;pdb.set_trace()
        # label = [0] * len(fea)
        # write_svm_data_file(label, fea, self.svm_dat_file)

        #### SAMPLE FEATURE TO REDUCE COMPUTATION TIME ####
        sample_fea = self.sample(fea, self.sample_ratio)
        # import pdb;pdb.set_trace()
        sample_fea = self.norm_fea(sample_fea)
        # sample_fea = self.pca(sample_fea)
        # import pdb;pdb.set_trace()
        label = [0] * len(sample_fea)
        write_svm_data_file(label, sample_fea, self.svm_dat_file)

    def detect(self, data):
        self.data_file = data
        self.write_dat(data)
        self.scale()
        self.train()
        self.predict()
        self.load_pred()

    def plot_pred(self, *args, **kwargs):
        # self.stat()
        fea_slice = self.get_start_time()
        min_t = float(fea_slice[0][0])
        start_time = [float(v[0])-min_t for v in fea_slice]
        y = []
        for i in xrange(len(start_time)):
            if self.pred[i] == self.ano_val:
                y.append(1)
            else:
                y.append(-1)
        x = [start_time[i] for i in xrange(len(start_time)) if self.pred[i] == self.ano_val]
        y = [1 for i in xrange(len(start_time)) if self.pred[i] == self.ano_val]
        # plt.plot(start_time, self.pred, '+')
        # threshold = [0] * len(start_time)
        plot_points(x, y,
                # threshold,
                ano_marker=['r+'], threshold_marker=None,
                *args, **kwargs)

        # plt.plot(x, y, '+r')
        # plt.axis([0, 2000, 0, 1.1])
        # if pic_show: plt.show()
        # if pic_name: plt.savefig(pic_name)

from util import DataEndException, FetchNoDataException
from PCA import PCA
try:
    import numpy as np
    NUMPY = True
except:
    NUMPY = False

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
                # fea = data_handler.get_svm_feature(rg=[time, time+self.win_size], rg_type=self.rg_type)
                fea = data_handler.get_svm_fea(rg=[time, time+self.win_size], rg_type=self.rg_type)
                fea_list.append(fea)
            except FetchNoDataException:
                print 'there is no data to detect in this window'
            except DataEndException:
                print 'reach data end, break'
                break

            time += self.interval

        self.detect_num = i - 1

        fea_list = self.norm_fea(fea_list)
        fea_list = self.pca(fea_list)
        # import pdb;pdb.set_trace()
        label = [0] * len(fea_list)
        write_svm_data_file(label, fea_list, self.svm_dat_file)

    # def train(self):
    #     print 'start to train...'
    #     subprocess.check_call([SVM_FOLDER + '/svm-train',
    #         '-s', '2',
    #         '-d', str(self.degree),
    #         '-n', str(self.nu),
    #         '-t', str(self.kernel_type),
    #         '-g', str(self.gamma),
    #         self.svm_dat_file,
    #         self.svm_model_file])

    def detect(self, data_handler):
        self.write_dat(data_handler)
        self.scale()
        self.train()
        self.predict()
        self.load_pred()

    # def plot_pred(self, pic_show=True, pic_name=None, *args, **kwargs):
    def plot_pred(self, *args, **kwargs):
        # import matplotlib.pyplot as plt
        # self.stat()
        ano_idx = [i for i in xrange(self.detect_num) if self.pred[i] == self.ano_val]
        x = [i*self.interval for i in ano_idx]
        y = [abs(self.pred[i]) for i in ano_idx]
        plot_points(x, y,
                ano_marker=['r+'], threshold_marker=None,
                *args, **kwargs)

        # plt.plot(x, y, '+r')
        # import pdb;pdb.set_trace()
        # plt.axis([0, 5000, 0, 1.1])
        # plt.axis([0, 2000, 0, 1.1])
        # if pic_show: plt.show()
        # if pic_name: plt.savefig(pic_name)



if __name__ == "__main__":
    desc = dict(gamma=0.1,
            svm_dat_file='./test.dat',
            svm_model_file='./test.model',
            svm_pred_file='./test.pred')
    detector = SVMFlowByFlowDetector(desc)
    detector.detect()
