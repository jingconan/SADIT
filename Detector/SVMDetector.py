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
    """SVM Detector"""
    def __init__(self, desc):
        self._defaults()
        self.__dict__.update(desc)

    def _defaults(self):
        self.svm_dat_file= settings.ROOT + '/res/test.dat'
        self.svm_model_file= settings.ROOT + '/res/test.model'
        self.svm_pred_file= settings.ROOT + '/res/test.pred'

        self.scale_para_file = settings.ROOT + '/res/scale.sf'

    def write_dat(self, data):
        fea = data.get_fea_slice()
        label = [0] * len(fea)
        write_svm_data_file(label, fea, self.svm_dat_file)

    def detect(self, data):
        self.data_file = data
        self.write_dat(data)

        print 'start to scale ...'
        scale_file = self.svm_dat_file + '.scale'
        subprocess.check_call(' '.join([SVM_FOLDER + '/svm-scale',
            '-s', self.scale_para_file,
            self.svm_dat_file,
            '>',
            scale_file
            ]), shell=True)
        self.svm_dat_file = scale_file


        print 'start to train...'
        subprocess.check_call([SVM_FOLDER + '/svm-train',
            '-s', '2',
            '-n', '0.001',
            '-g', str(self.gamma),
            self.svm_dat_file,
            self.svm_model_file])

        print 'start to predict...'
        subprocess.check_call([SVM_FOLDER + '/svm-predict',
            self.svm_dat_file,
            self.svm_model_file,
            self.svm_pred_file])

        self.load_pred()

    def load_pred(self):
        fid = open(self.svm_pred_file)
        self.pred = []
        while True:
            line = fid.readline()
            if not line: break
            self.pred.append(int(line))
        fid.close()

    def stat(self):
        pos = len([1 for v in self.pred if v == 1])
        neg = len([-1 for v in self.pred if v == -1])
        print 'pos, ', pos, 'neg, ', neg
        pass

    def plot_pred(self, pic_show=True, pic_name=None):
        import matplotlib.pyplot as plt
        fea_slice = self.data_file.data.get_fea_slice(fea=['start_time'])
        min_t = float(fea_slice[0][0])
        start_time = [float(v[0])-min_t for v in fea_slice]
        x = [start_time[i] for i in xrange(len(start_time)) if self.pred[i] == -1]
        y = [1 for i in xrange(len(start_time)) if self.pred[i] == -1]
        # plt.plot(start_time, self.pred, '+')
        plt.plot(x, y, '+')
        if pic_show: plt.show()
        if pic_name: plt.savefig(pic_name)


if __name__ == "__main__":
    desc = dict(gamma=0.1,
            svm_dat_file='./test.dat',
            svm_model_file='./test.model',
            svm_pred_file='./test.pred')
    detector = SVMDetector(desc)
    detector.detect()
