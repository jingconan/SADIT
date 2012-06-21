#!/usr/bin/env python
from DataParser import RawParseData

######################################
##     Utility Function            ###
######################################
def binary_search(a, x, lo=0, hi=None):
    """
    Find the index of largest value in a that is smaller than x.
    a is sorted Binary Search
    """
    # import pdb;pdb.set_trace()
    if hi is None: hi = len(a)
    while lo < hi:
        mid = (lo + hi) / 2
        midval = a[mid]
        if midval < x:
            lo = mid + 1
        elif midval > x:
            hi = mid
        else:
            return mid
    return hi-1

Find = binary_search

def _to_tuple(ip):
    return tuple( [int(v) for v in ip.rsplit('.')] )

# The Distance Function
DF = lambda x,y:abs(x[0]-y[0]) * (256**3) + abs(x[1]-y[1]) * (256 **2) + abs(x[2]-y[2]) * 256 + abs(x[3]-y[3])

def write_svm_data_file(label, fea, f_name):
    fid = open(f_name, 'w')
    assert(len(label) == len(fea))
    n = len(label)
    for i in xrange(n):
        fea_v = fea[i]
        line = ['%s:%s'%(j+1, fea_v[j]) for j in xrange(len(fea_v)) ]
        fid.write(str(label[i]) + ' ' + ' '.join(line) + '\n')

from ClusterAlg import KMeans
from subprocess import call
SVM_FOLDER = '/home/wangjing/LocalResearch/CyberSecurity/taylor/svm_detector/libsvm-3.12/'
def flow_by_flow_svm(normal_file, abnormal_file, cluster_num, gamma):
    f_all, fea_name = RawParseData(normal_file)

    zip_f_all = zip(*f_all)
    ip_str = zip_f_all[fea_name.index('src_ip')]
    ip_tuple = [ _to_tuple(ip) for ip in ip_str ]
    n = len(ip_str)

    cluster, center_pts = KMeans(ip_tuple, cluster_num, DF)
    dist_to_center = [ DF(ip_tuple[i], center_pts[cluster[i]]) for i in xrange(n) ]
    flow_size = zip_f_all[fea_name.index('flow_size')]

    f_anom, fea_name2 = RawParseData(abnormal_file)
    assert(fea_name == fea_name2)
    ano_flow_idx = [f_all.index(f) for f in f_anom]
    label = [0] * n
    for idx in ano_flow_idx:
        label[idx] = -1
    DATA_FILE = './test.dat'
    MODEL_FILE = './test.model'
    PRED_FILE = './test.pred'
    write_svm_data_file(label, zip(*[cluster, dist_to_center, flow_size]), DATA_FILE)
    call([SVM_FOLDER + 'svm-train',
        '-s', '2',
        '-n', '0.001',
        '-g', str(gamma),
        DATA_FILE,
        MODEL_FILE])

    call([SVM_FOLDER + 'svm-predict',
        DATA_FILE,
        MODEL_FILE,
        PRED_FILE])

    # call([SVM_FOLDER + 'svm_predict',
        # DATA_FILE,
        # MODEL_FILE,
        # PRED_FILE])

from collections import Counter
def hist(data, poss_val_list):
    c = Counter(data)
    return [c.get(v, 0) for v in poss_val_list]

def svm(normal_file, abnormal_file, win_size, interval, gamma):
    f_all = RawParseData(normal_file)
    f_anom = RawParseData(abnormal_file)

    t = [ float(f['start_time']) for f in f_all ]
    ip = [ f['src_ip'] for f in f_all ]
    ip_list = list( set(ip) )
    # n = len(f_all)
    tteststop  = float(f_anom[-1]['start_time'])

    # slide the window, for 'time'
    while True:
        win_start_idx = Find(t, win_start_t)
        win_end_idx = Find(t, win_end_t)
        ip_hist = hist( ip[win_start_idx:win_end_idx] )
        win_start_t += interval
        win_end_t = win_start_t + win_size
        pass

    # tteststop  = float(f_anom[-1]['start_time'])
    # for i in xrange(n):
        # if f_all[i]['start_time'] > tteststop:
            # iteststop = i
    # itrainstart = iteststop + 1


    # build training set
    ntrain = n - itrainstart + 1;

    itrain = 1;




# def SVMDetector(object):
    # def __init__(self):
        # pass

def test():
    pass

if __name__ == "__main__":
    flow_by_flow_svm('../data/n0_flow.txt', '../data/abnormal_n0_flow.txt', 2, 0.01)
