"""
This file defines useful APIs for other modules or program to use
"""
from __future__ import print_function, division
#######################################################
###        Import Detectors                        ####
#######################################################
# from StoDetector import ModelFreeAnoDetector, ModelBaseAnoDetector, FBAnoDetector
# from StoDetector import TwoWindowAnoDetector, PeriodStoDetector
# from StoDetector import AutoSelectStoDetector
# from StoDetector import ExpectedStoDetector
# from RobustDetector import RobustDetector

# from SVMDetector import SVMFlowByFlowDetector, SVMTemporalDetector
from StoDetector import *
from RobustDetector import *
from SVMDetector import *

from ART.ART import ARTDetector

# detector_map defines correspondence between detector
# options with detector name
detector_map = {
        # 'auto': AutoSelectStoDetector,
        # '2w': TwoWindowAnoDetector,
        'two_win': TwoWindowAnoDetector,
        # 'ada':AdaStoDetector,
        'period': PeriodStoDetector,
        'speriod': PeriodStaticDetector,
        'mf': ModelFreeAnoDetector,
        'mb': ModelBaseAnoDetector,
        'mfmb': FBAnoDetector,
        'svm_fbf': SVMFlowByFlowDetector,
        'svm_temp': SVMTemporalDetector,
        'art': ARTDetector,
        'gen_fb_mf':FBAnoDetector, # feature is model free emperical measure
        'gen_fb_mb':FBAnoDetector, # feature is model based emperical measure
        # 'robust': RobustDetector,
        }

# usually one detector corresponds to one handler
# handlers do some data preprocessing for detector.
from DataHandler import *
data_handler_handle_map = {
        'robust': QuantizeDataHandler,
        # 'auto': QuantizeDataHandler,
        'mf': QuantizeDataHandler,
        'mb': QuantizeDataHandler,
        'mfmb': QuantizeDataHandler,
        # '2w': QuantizeDataHandler,
        'two_win': QuantizeDataHandler,
        # 'ada': QuantizeDataHandler,
        'period': QuantizeDataHandler,
        'speriod': QuantizeDataHandler,
        'svm_temp': SVMTemporalHandler,
        'svm_fbf':QuantizeDataHandler,
        'art': FakeDataHandler,

        'gen_fb_mf':ModelFreeFeaGeneralizedEMHandler, # feature is model free emperical measure
        'gen_fb_mb':ModelBasedFeaGeneralizedEMHandler, # feature is model based emperical measure
        # 'expect':QuantizeGeneralizedEMHandler,
        }

from Data import *
data_map = {
        'fs': PreloadHardDiskFile,
        'pcap2netflow': PreloadHardDiskFile_pcap2netflow,
        'xflow': PreloadHardDiskFile_xflow,
        'SQLFile_SperottoIPOM2009': SQLFile_SperottoIPOM2009,
        'flow_exporter': PreloadHardDiskFile_FlowExporter,
        }

def print_detector_help(type_):
    """print help message of detector with type_
    """
    detector = detector_map[ type_ ]({})
    detector.set_args(['-h'])

def detect(f_name, desc, res_args=[]):
    """An function for convenience
    - *f_name* the name or a list of name for the flow file.
    - *desc* is a parameter dictionary
    """
    # win_size = desc['win_size']
    fea_option = desc['fea_option']
    data_file = data_map[ desc['data_type'] ](f_name)
    # data_handler = data_handler_handle_map[desc['detector_type']](data_file, fea_option)
    data_handler = data_handler_handle_map[desc['method']](data_file, desc)

    detector = detector_map[ desc['method'] ](desc)
    detector.set_args(res_args)
    detector.detect(data_handler)
    return detector

def detector_plot_dump(data_name, type_, desc, *args, **kwargs):
    """don't actually detect, only plot precalculated data
    """
    detector = detector_map[type_](desc)
    detector.set_args([])
    detector.plot_dump(data_name, *args, **kwargs)

def test_detect():
    ANO_ANA_DATA_FILE = './test_AnoAna.txt'
    DETECTOR_DESC = dict(
            interval=20,
            win_size=400,
            win_type='time', # 'time'|'flow'
            fr_win_size=100, # window size for estimation of flow rate
            false_alarm_rate = 0.001,
            unified_nominal_pdf = False, # used in sensitivities analysis
            fea_option = {'dist_to_center':2, 'flow_size':2, 'cluster':2},
            ano_ana_data_file = ANO_ANA_DATA_FILE,
            detector_type = 'mfmb',
            data_handler = 'fs',
            )
    desc = DETECTOR_DESC
    detector = detect('../Simulator/n0_flow.txt', desc)
    detector.plot_entropy()

if __name__ == "__main__":
    test_detect()
