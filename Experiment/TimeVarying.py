#!/usr/bin/env python
""" Experiment For Time Varying Traffic
Will generate traffic based on existing flow records, just change
the flow size based on some distribution.

Detect the results and save some some folder
"""
from __future__ import print_function
import sys
sys.path.insert(0, '..')
import os

from util import mkiter, meval
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
def tran_flow_size_to_time_varying(f_name, out_f_name, transform,
        data_pic_name):
    """ tranform flow size in the flow record to be time_varying model
    """
    flows,  keys = RawParseData(f_name)
    zip_flows = zip(*flows)
    t_idx = keys.index('start_time')
    fs_idx = keys.index('flow_size')
    t = [float(vt) for vt in zip_flows[t_idx]]
    mint = min(t)
    nt = [v_ - mint for v_ in t]

    flow_size = [float(fs) for fs in zip_flows[fs_idx]]
    fig = plt.figure()
    ax1 = fig.add_subplot(211)
    plt.plot(nt, flow_size, axes=ax1)
    new_flow_size = transform(t, flow_size)
    zip_flows[fs_idx] = [str(fs) for fs in new_flow_size]
    ax2 = fig.add_subplot(212)
    plt.plot(nt, new_flow_size, axes=ax2)
    # plt.savefig('scene.pdf')
    plt.savefig(data_pic_name)
    # plt.show()

    flows = zip(*zip_flows)
    write_file(out_f_name, FS_FORMAT, flows, keys)

from math import sin, pi
def tran_sin(t, x, M, T, phase):
    mint = min(t)
    y = [vx + M * sin( 2*pi / T * (vt-mint) + phase) for vt, vx in zip(t, x)]
    return y

from IIDExper import IIDExper, load_para
from Detector import detect
from itertools import product
class TimeVarying(IIDExper):
    def init_parser(self, parser):
        super(TimeVarying, self).init_parser(parser)
        parser.add_argument('--M', default=0, type=meval,
                help = """amplitude of the sine time varying normal traffic""")
        parser.add_argument('--T', default=0, type=meval,
                help = """period of the sine time varying normal traffic""")
        parser.add_argument('--phase', default=0, type=meval,
                help = """phase of the sine time varying normal traffic""")

        parser.add_argument('--res_folder', default='./res',
                help = """res folder""")
        parser.add_argument('--pad_len', default=7 ,
                help = """pad the file names with leading zeros to the samd
                length so that the
                order is correct""")

    def detect(self, data, pic_name):
        args = self.args
        res_args = self.res_args
        default_settings = load_para(args.default_settings)
        desc = default_settings['DETECTOR_DESC']
        if args.data_type: desc['data_type'] = args.data_type
        if args.feature_option: desc['fea_option'] = eval(args.feature_option)
        if args.method: desc['detector_type'] = args.method

        # import pdb;pdb.set_trace()
        detector = detect(os.path.abspath(data), desc, res_args)
        detector.plot(pic_show=False,
                pic_name=pic_name,
                csv=pic_name+'.csv')

        self.detector = detector
        return self.detector


    def run(self):
        if not self.args.no_sim:
            self.configure()
            self.simulate()

        if not os.path.exists(self.args.res_folder):
            os.makedirs(self.args.res_folder)
        args = self.args
        D = args.pad_len
        M = mkiter(args.M)
        T = mkiter(args.T)
        phase = mkiter(self.args.phase)
        for m, tt, ph in product(M, T, phase):
            prefix = '%s/%s_M_%0*d_T_%0*d_ph_%0*f_'%(args.res_folder,
                    args.method,
                    D, m,
                    D, tt, D, ph)
            out_f_name = prefix + 'flow.txt'
            data_pic_name = prefix + 'pic.png'
            res_pic_name = prefix + 'res.png'
            tran_flow_size_to_time_varying(self.output_flow_file,
                    out_f_name,
                    lambda t, x:tran_sin(t, x, m, tt, ph),
                    data_pic_name,
                    )
            self.detect(out_f_name, res_pic_name)

        return self.detector
