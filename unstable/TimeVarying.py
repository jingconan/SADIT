#!/usr/bin/env python
""" Experiment For Time Varying Traffic
Will generate traffic based on existing flow records, just change
the flow size based on some distribution.
"""
from __future__ import print_function
import sys
sys.path.insert(0, '..')

# def
from Detector.DataParser import RawParseData

# FORMAT of FS output file
FS_FORMAT = dict(start_time=3, end_time=4, src_ip=5, sc_port=6, flow_size=13, )

def write_file(f_name, format_, flows, keys):
    f_id = open(f_name, 'w')
    max_item_num = max(format_.values()) + 1
    for f in flows:
        line_list = ['_'] * max_item_num
        line_list[0] = 'textexport'
        for k, v in format_.iteritems():
            line_list[v] = f[keys.index(k)]
        f_id.write(' '.join(line_list) + '\n')

    f_id.close()

import matplotlib.pyplot as plt
def tran_flow_size_to_time_varying(f_name, out_f_name, transform):
    """ tranform flow size in the flow record to be time_varying model
    """
    flows,  keys = RawParseData(f_name)
    zip_flows = zip(*flows)
    t_idx = keys.index('start_time')
    fs_idx = keys.index('flow_size')
    t = [float(vt) for vt in zip_flows[t_idx]]
    flow_size = [float(fs) for fs in zip_flows[fs_idx]]
    fig = plt.figure()
    ax1 = fig.add_subplot(211)
    plt.plot(t, flow_size, axes=ax1)
    new_flow_size = transform(t, flow_size)
    zip_flows[fs_idx] = [str(fs) for fs in new_flow_size]
    ax2 = fig.add_subplot(212)
    plt.plot(t, new_flow_size, axes=ax2)
    plt.savefig('scene.pdf')
    plt.show()

    flows = zip(*zip_flows)
    write_file(out_f_name, FS_FORMAT, flows, keys)

from math import sin, pi
def tran_sin(t, x):
    mint = min(t)
    M = 1e3
    # M = 2e3
    # T = 1000
    T = 8000
    shift = pi/2
    y = [vx + M * sin( 2*pi / T * (vt-mint) + shift ) for vt, vx in zip(t, x)]
    return y

if __name__ == "__main__":
    # transform = lambda x, y: y
    # tran_flow_size_to_time_varying('../Simulator/n0_flow.txt', tran_sin)

    # tran_flow_size_to_time_varying(
            # '../../CyberSecurity/ARO_demo/data/flow_size_mean_2x_t_5000s_anomaly_1000s_to_1300s/n0_flow.txt',
            # '../../CyberSecurity/time_varying/data/n0_flow_M_2e3_T_1e3.txt', tran_sin)

    # tran_flow_size_to_time_varying(
            # '../../CyberSecurity/ARO_demo/data/flow_size_mean_2x_t_5000s_anomaly_1000s_to_1300s/n0_flow.txt',
            # '../../CyberSecurity/time_varying/data/n0_flow_M_2e3_T_4e3.txt', tran_sin)

    tran_flow_size_to_time_varying(
            '../../CyberSecurity/ARO_demo/data/flow_size_mean_2x_t_5000s_anomaly_1000s_to_1300s/n0_flow.txt',
            './test.txt', tran_sin)




