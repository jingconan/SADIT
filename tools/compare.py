"""
compare the result of sadit detector and other detectors
for example, Dan's algorithm
"""
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

def read_dan_data(fname):
    FORMAT = dict(seq=[2, int], flow_size=[5, float], ip_dist=[9, float])
    return read_data(fname, FORMAT)

def read_sadit_data(fname):
    FORMAT = dict(seq=[2, int], cluster=[5, lambda x: int(float(x))],
            dist_to_center=[8, float], flow_size=[11, float])
    return read_data(fname, FORMAT)

if __name__ == "__main__":
    res_sadit, fea_list_sadit = read_sadit_data('/home/wangjing/LocalResearch/CyberData/res-2003/mb-cluster_6.txt')
    res_dan, fea_list_dan = read_dan_data('../../CyberData/Dan/anomolies20030902_07.txt')
    zip_res_sadit = zip(*res_sadit)
    zip_res_dan = zip(*res_dan)
    seq_anomaly_sadit = zip_res_sadit[fea_list_sadit.index('seq')]
    seq_anomaly_dan = zip_res_dan[fea_list_dan.index('seq')]
    ins = set.intersection(set(seq_anomaly_sadit), set(seq_anomaly_dan))
    uns = set.union(set(seq_anomaly_sadit), seq_anomaly_dan)

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
    print 'ration is: %f'%(len(ins) * 1.0 / len(uns))




