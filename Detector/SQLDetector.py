#!/usr/bin/env python
"""
Detection Algorithm Using the SQL Server instead of low file.
support:
    - Mysql
"""
__author__ = "Jing Conan Wang"
__email__ = "wangjing@bu.edu"
__status__ = "Development"

import sys
sys.path.append("..")
from AnomalyDetector import ModelFreeAnoDetector, ModelBaseAnoDetector, FBAnoDetector
from SQLDataFile import SQLDataFileHandler_SperottoIPOM2009
def detect(db_info, detector_type, detector_desc):
    """An function for convenience
    - *db_info* information of database
    - *win_size* the window size
    - *fea_option*

    """
    detector_map = {
            'mf':ModelFreeAnoDetector,
            'mb':ModelBaseAnoDetector,
            'mfmb':FBAnoDetector,
            }
    data_file = SQLDataFileHandler_SperottoIPOM2009(db_info,
            detector_desc['win_size'],
            detector_desc['fea_option'])
    detector = detector_map[detector_type](detector_desc)
    detector(data_file,
            detector_desc['norminal_rg'],
            detector_desc['win_type'],
            detector_desc['max_detect_num'])
    return detector


if __name__ == "__main__":
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
            max_detect_num = 100,
            norminal_rg = [0, 1000],
            )
    detector = detect(db_info, 'mfmb', detector_desc)
    import pdb;pdb.set_trace()
    # import pdb;pdb.set_trace()
    detector.plot_entropy()
