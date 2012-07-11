#!/usr/bin/env python
"""
compare the result of sadit detector and other detectors
for example, Dan's algorithm
"""
from parse import *
# read Dan's Data
import os

def read_data(fname, FORMAT):
    fid = open(os.path.abspath(fname), 'r')
    abnormal_flows = []
    res = []
    while True:
        l = []
        line = fid.readline()
        if not line: break
        if not line.startswith('Sample #'):
            continue
        attr_list = line.split()
        res.append( [_type(attr_list[pos]) for pos, _type in FORMAT.values()] )

    return res, FORMAT.keys()


class CompareResult(object):
    """Compare detection result of Jing's SADIT with Dan's Approach"""
    def __init__(self):
        self.jing_data = dict()
        self.dan_data = dict()
        pass

    def load_jing_data(self, fname):
        data, fea_list = parse_xflow(fname)
        self.jing_data['data'] = data
        self.jing_data['fea_list'] = fea_list
        self.jing_data['col_data'] = dict( zip(fea_list, zip(*data)) )

    def load_dan_data(self, fname):
        FORMAT = dict(
                seq=[2, int],
                # flow_size=[5, float],
                # Cb=[5, float],
                client_ip = [6, str],
                server_ip = [10, str],
                Cb=[13, float],
                )
        data, fea_list = read_data(fname, FORMAT)
        self.dan_data['data'] = data
        self.dan_data['fea_list'] = fea_list
        self.dan_data['col_data'] = dict( zip(fea_list, zip(*data)) )

    def get_intersection_ratio(self, A, B):
        self.ins = set.intersection(set(A), set(B))
        self.uns = set.union(set(A), B)
        return len(self.ins) * 1.0 / len(self.uns)


    def compare_attr(self, attr):
        if isinstance(attr, list):
            jing_sets = set( zip(*tuple([self.jing_data['col_data'][a] for a in attr])) )
            dan_sets = set( zip(*tuple([self.dan_data['col_data'][a] for a in attr])) )
        elif isinstance(attr, str):
            jing_sets = set(self.jing_data['col_data'][attr])
            dan_sets = set(self.dan_data['col_data'][attr])
        else: raise Exception("unknown attr")
        r = self.get_intersection_ratio(jing_sets, dan_sets)
        print 'intersection ratio for attribute %s is: %f'%(attr, r)
        print 'len of attr %s jing: %i'%(attr, len(jing_sets))
        print 'len of attr %s dan: %i' %(attr, len(dan_sets))
        print 'the number of intersection set is: %i'%(len(self.ins))
        print 'the number of union set is: %i'%(len(self.uns))
        print 'len of ins over jing %f'%(len(self.ins) * 1.0 / len(jing_sets))
        print 'len of ins over dan %f'%(len(self.ins) * 1.0 / len(dan_sets))


    def compare(self):
        self.compare_attr(['client_ip', 'Cb'])
        pass


# def read_dan_data(fname):
#     FORMAT = dict(seq=[2, int], flow_size=[5, float], ip_dist=[9, float])
#     return read_data(fname, FORMAT)

# def read_sadit_data(fname):
#     FORMAT = dict(seq=[2, int], cluster=[5, lambda x: int(float(x))],
#             dist_to_center=[8, float], flow_size=[11, float])
#     return read_data(fname, FORMAT)

def back_main():
    # res_sadit, fea_list_sadit = read_sadit_data('/home/wangjing/LocalResearch/CyberData/res-2003/mb-cluster_6.txt')
    # res_sadit, fea_list_sadit = read_sadit_data('../res/mb-cluster_6.txt')
    # res_sadit, fea_list_sadit = read_sadit_data('../../CyberData/sadit_res/res/mb-cluster_4.txt')
    # res_sadit, fea_list_sadit = read_sadit_data('../res/mb-cluster_4-formated.txt')
    # res_dan, fea_list_dan = read_dan_data('../../CyberData/Dan/anomolies20030902_07.txt')
    # res_dan, fea_list_dan = read_dan_data('../../CyberData/Dan/anomolies20030902_07.txt')
    res_dan, fea_list_dan = read_dan_data('../../CyberData/Dan/anomolies20030902_07.txt')
    zip_res_sadit = zip(*res_sadit)
    zip_res_dan = zip(*res_dan)
    seq_anomaly_sadit = zip_res_sadit[fea_list_sadit.index('seq')]
    seq_anomaly_dan = zip_res_dan[fea_list_dan.index('seq')]
    ins = set.intersection(set(seq_anomaly_sadit), set(seq_anomaly_dan))
    uns = set.union(set(seq_anomaly_sadit), seq_anomaly_dan)

    print 'ration is: %f'%(len(ins) * 1.0 / len(uns))
    for i in ins:
        idx_sadit = seq_anomaly_sadit.index(i)
        idx_dan = seq_anomaly_dan.index(i)
        flow_size_sadit = res_sadit[idx_sadit][fea_list_sadit.index('flow_size')]
        flow_size_dan = res_dan[idx_dan][fea_list_dan.index('flow_size')]
        flow_size_danp1 = res_dan[idx_dan+1][fea_list_dan.index('flow_size')]
        flow_size_danm1 = res_dan[idx_dan-1][fea_list_dan.index('flow_size')]
        print 'i, ', i
        print 'flow_size_sadit', flow_size_sadit
        print 'flow_size_dan', flow_size_dan
        print 'flow_size_danp1', flow_size_danp1
        print 'flow_size_danm1', flow_size_danm1
        assert( flow_size_sadit == flow_size_dan )



if __name__ == "__main__":
    com = CompareResult()
    # com.load_jing_data('../res/mb-cluster_6-raw.txt')
    # com.load_dan_data('../../CyberData/Dan2/anomolies2003.txt')
    com.load_dan_data('../../CyberData/Dan2/anomolies2003_2.txt')
    # com.load_dan_data('../../CyberData/Dan2/anomolies2007.txt')
    jing_path = '../res/'
    dir_list = os.listdir(jing_path)
    file_list = [f for f in dir_list if f.endswith('raw.txt')]
    for f in file_list:
        print '-' * 40
        print "result for jing's ", f
        com.load_jing_data(jing_path + f)
        com.compare()

