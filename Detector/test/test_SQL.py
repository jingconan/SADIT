#!/usr/bin/env python
import sys
sys.path.append("..")
sys.path.append("../..")

from Detector import *
def test_SQL():
    db_info = dict(
            host = "localhost",
            db = "labeled",
            read_default_file = "~/.my.cnf",
            )

    ANO_ANA_DATA_FILE = '~/Share/AnoAna.txt'
    detector_desc = dict(
            # interval=30,
            # interval=50,
            # win_size = 50,
            interval=20,
            # win_size = 10,
            win_size=400,
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
            normal_rg = [0, 8000],
            )
    detector = detect_sql(db_info, 'mfmb', detector_desc)
    detector.plot_entropy(pic_show=False, pic_name="./test_SQL.eps")
    # import pdb;pdb.set_trace()

if __name__ == "__main__":
    test_SQL()
