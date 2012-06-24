#!/usr/bin/env python
import sys
sys.path.append("..")
sys.path.append("../..")
from Detector import *

def test_xflow_2003():
    ANO_ANA_DATA_FILE = './test_AnoAna.txt'
    DETECTOR_DESC = dict(
            interval=5000,
            win_size = 4000,
            win_type='flow', # 'time'|'flow'
            fr_win_size=100, # window size for estimation of flow rate
            false_alarm_rate = 0.001,
            unified_nominal_pdf = False, # used in sensitivities analysis
            fea_option = {'dist_to_center':2, 'flow_size':2, 'cluster':2},
            ano_ana_data_file = ANO_ANA_DATA_FILE,
            detector_type = 'mfmb',
            normal_rg = None,
            max_detect_num = None,
            data_handler = 'xflow',
            )
    desc = DETECTOR_DESC

    f_name ='../../../20030902.07.flow.txt'
    detector = detect(f_name, desc)
    detector.plot_entropy(pic_show=False, pic_name="./test_pcap2netflow_loc3.eps")

if __name__ == "__main__":
    # test_pcap2netflow()
    import time
    start_t = time.clock()
    test_xflow_2003()
    end_t = time.clock()
    print 'total running time is: %f'%(end_t - start_t)



