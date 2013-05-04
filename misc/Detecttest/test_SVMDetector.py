#!/usr/bin/env python
from __future__ import print_function, division, absolute_import
from ..Detector.DataHandler import HardDiskFileHandler
from ..Detector.SVMDetector import SVMFlowByFlowDetector, SVMTemporalDetector, SVMTemporalHandler
import settings

def test_SVMFlowByFlowDetector():
    detector_desc = dict(
            gamma = 0.001,
            fea_option = {'dist_to_center':2, 'flow_size':2, 'cluster':2},
            )

    fname = settings.ROOT + '/Simulator/n0_flow.txt'
    data_file = HardDiskFileHandler(
            fname = fname,
            fea_option = detector_desc['fea_option']
            )

    detector = SVMFlowByFlowDetector(detector_desc)
    detector.detect(data_file)
    # detector.stat()
    detector.plot_pred()

def test_SVMTemporalDetector():
    detector_desc = dict(
            gamma = 0.001,
            fea_option = {'dist_to_center':2, 'flow_size':2, 'cluster':2},
            max_detect_num = None,
            # rg_type = 'flow',
            rg_type = 'time',
            win_size = 100,
            interval = 20,
            )

    fname = settings.ROOT + '/Simulator/n0_flow.txt'
    # data_handler = HardDiskFileHandler(
            # fname = fname,
            # fea_option = detector_desc['fea_option']
            # )
    data_handler = SVMTemporalHandler(
            fname = fname,
            )



    detector = SVMTemporalDetector(detector_desc)
    detector.write_dat(data_handler)
    detector.detect(data_handler)
    # detector.stat()
    detector.plot_pred()


if __name__ == "__main__":
    # test_SVMFlowByFlowDetector()
    test_SVMTemporalDetector()
