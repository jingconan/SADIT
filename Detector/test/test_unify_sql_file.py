#!/usr/bin/env python
from __future__ import print_function, division, absolute_import
from ..DataFile import HardDiskFileHandler
if __name__ == "__main__":
    from AnomalyDetector import FBAnoDetector
    ANO_ANA_DATA_FILE = '~/Share/AnoAna.txt'
    detector_desc = dict(
            # interval=30,
            # interval=50,
            # win_size = 50,
            interval=20,
            # win_size = 10,
            win_size=200,
            win_type='time', # 'time'|'flow'
            fr_win_size=100, # window size for estimation of flow rate
            false_alarm_rate = 0.001,
            unified_nominal_pdf = False, # used in sensitivities analysis
            # discrete_level = DISCRETE_LEVEL,
            # cluster_number = CLUSTER_NUMBER,
            # fea_option = {'dist_to_center':2, 'flow_size':2, 'cluster':2},
            fea_option = {'dist_to_center':2, 'octets':2, 'cluster':2},
            # fea_option = {'dist_to_center':2, 'flow_size':2, 'cluster':1},
            ano_ana_data_file = ANO_ANA_DATA_FILE,
            detector_type = 'mfmb',
            max_detect_num = 400,
            norminal_rg = [0, 1000],
            )

    f_name = '../Simulator/n0_flow.txt'
    data_file = HardDiskFileHandler(f_name,
            detector_desc['win_size'],
            detector_desc['fea_option'])

    detector = FBAnoDetector(detector_desc)
    detector.detect(data_file,
            detector_desc['norminal_rg'],
            detector_desc['win_type'],
            detector_desc['max_detect_num'])
    detector.plot_entropy()
