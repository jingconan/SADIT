#!/usr/bin/env python
import sys
sys.path.insert(0, '../../')
from Detector.DataHandler import HardDiskFileHandler
from Detector.SVMDetector import SVMDetector
import settings

def test_SVMDetector():
    detector_desc = dict(
            gamma = 0.001,
            fea_option = {'dist_to_center':2, 'flow_size':2, 'cluster':2},
            )

    fname = settings.ROOT + '/Simulator/n0_flow.txt'
    data_file = HardDiskFileHandler(
            fname = fname,
            fea_option = detector_desc['fea_option']
            )

    detector = SVMDetector(detector_desc)
    detector.detect(data_file)
    detector.stat()
    detector.plot_pred()

if __name__ == "__main__":
    test_SVMDetector()
