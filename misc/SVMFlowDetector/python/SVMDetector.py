"""
This file is the flow by flow svm detector
"""

# Local Settings
LIB_PATH = '../../'
SVM_FOLDER = '../libsvm-3.12'

import sys
sys.path.insert(0, LIB_PATH)
from subprocess import call

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
        self.__dict__.update(desc)

    def write_dat(self, data):
        fea = data.get_fea_slice()
        label = [0] * len(fea)
        write_svm_data_file(label, fea, self.svm_dat_file)

    def detect(self, data):
        self.write_dat(data)
        call([SVM_FOLDER + 'svm-train',
            '-s', '2',
            '-n', '0.001',
            '-g', str(self.gamma),
            self.svm_dat_file,
            self.svm_model_file])


        call([SVM_FOLDER + 'svm-predict',
            self.svm_dat_file,
            self.svm_model_file,
            self.svm_pred_file])


if __name__ == "__main__":
    desc = dict(gamma=0.1,
            svm_dat_file='./test.dat',
            svm_model_file='./test.model',
            svm_pred_file='./test.pred')
    detector = SVMDetector(desc)
    detector.detect()
