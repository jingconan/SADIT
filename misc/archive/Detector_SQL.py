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
from Detector_basic import ModelFreeAnoDetector, ModelBaseAnoDetector, FBAnoDetector
from SQLDataFile import SQLDataFileHandler_SperottoIPOM2009
def detect_sql(db_info, detector_type, detector_desc):
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
    detector.detect(data_file)
    return detector
