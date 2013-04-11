#!/usr/bin/env python
""" Argument Search script for optimal parameters for stochastic
method [model free and model based] methdod.
"""
import linecache
import os
from Detect import Detect
from Batch import Batch
from Detector import detect


def copy_lines(from_file, to_file, line_indices):
    """  copy lines in a file to a new file

    Parameters:
    ---------------
    from_file, to_file : str
       file name of the source and destination
    line_indices : list
        list of indices for the lines that will be copied

    Returns:
        None

    --------------
    """
    with open(to_file, 'w') as fid:
        for idx in line_indices:
            line = linecache.getline(from_file, idx)
            fid.write(line)

class DetectBatch(Batch):
    """
    Run Detect with different parameters in a batch mode.
    """
    def __init__(self, *args, **kwargs):
        exper = Detect(*args, **kwargs)
        super(DetectBatch, self).__init__(exper, *args, **kwargs)

    def export_ab_flow_raw(self, flow_file, output_file, *args, **kwargs):
        dirname = os.path.dirname(output_file)
        basename = os.path.basename(output_file)

        ab_flow_seq = self.exper.detector.get_ab_flow_seq('mf', *args, **kwargs)
        copy_lines(flow_file, dirname + '/mf-' + basename, ab_flow_seq)

        ab_flow_seq = self.exper.detector.get_ab_flow_seq('mb', *args, **kwargs)
        copy_lines(flow_file, dirname + '/mb-' + basename, ab_flow_seq)

    def export_ident_flow(self, fname, entropy_type, desc):
        """instead of exportoing all flows in the suspicious window,
        **export_ident_flow** will export flows only when flows are in anomalous state"""
        flow_state = self.exper.detector.ident(entropy_type=entropy_type,
                entropy_threshold = desc['entropy_threshold'],
                ab_win_portion = desc['ab_win_portion'],
                ab_win_num = desc['ab_win_num'],
                **desc['ident'][entropy_type]
                )
        ab_flow_seq = self.exper.detector.get_ab_flow_seq(entropy_type, ab_flow_info=flow_state,
                entropy_threshold = desc['entropy_threshold'],
                ab_win_portion = desc['ab_win_portion'],
                ab_win_num = desc['ab_win_num'],
                )
        dirname = os.path.dirname(fname)
        basename = os.path.basename(fname)
        # self._export_ab_flow_by_idx(desc['flow_file'],
        copy_lines(desc['data'],
                dirname + '/%s-'%(entropy_type) + basename,
                ab_flow_seq)

    def export(self, prefix, desc):
        """export outputs

        export
            1. raw flow records
            2. abnormal flows export output by detector
            3. a small set of abnormal flows filtered by FlowStateIdentification techniques.
        """
        self.exper.desc = desc
        self.exper.detector = detect(desc['data'], desc)

        # self.exper.detector.plot_entropy(False, prefix+'.eps')
        self.exper.detector.plot(pic_name = prefix+'.eps')


        self.export_ab_flow_raw(
                flow_file = desc['data'],
                output_file = prefix+'-raw.txt',
                entropy_threshold = desc['entropy_threshold'],
                ab_win_portion = desc['ab_win_portion'],
                ab_win_num = desc['ab_win_num'],
                )

        self.exper.detector.export_abnormal_flow(
                prefix+'-formated.txt',
                entropy_threshold = desc['entropy_threshold'],
                ab_win_portion = desc['ab_win_portion'],
                ab_win_num = desc['ab_win_num'],
                )

        self.export_ident_flow(prefix+'-ident.txt', 'mf', desc)
        self.export_ident_flow(prefix+'-ident.txt', 'mb', desc)


if __name__ == "__main__":
    import doctest
    doctest.testmod()
