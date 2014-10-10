""" This file defines useful APIs for other modules or program to use
"""
from __future__ import print_function, division, absolute_import
#######################################################
###        Import Detectors                        ####
#######################################################
from .StoDetector import *
from .RobustDetector import *
from .SVMDetector import *

from .ART.ART import ARTDetector

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
        'robust': RobustDetector,
        }

# usually one detector corresponds to one handler
# handlers do some data preprocessing for detector.
from .DataHandler import *
data_handler_handle_map = {
        'robust': FBQuantizeDataHandler,
        # 'auto': QuantizeDataHandler,
        'mf': ModelFreeQuantizeDataHandler,
        'mb': ModelBasedQuantizeDataHandler,
        'mfmb': FBQuantizeDataHandler,
        # '2w': QuantizeDataHandler,
        'two_win': FBQuantizeDataHandler,
        # 'ada': QuantizeDataHandler,
        'period': FBQuantizeDataHandler,
        'speriod': QuantizeDataHandler,
        'svm_temp': SVMTemporalHandler,
        'svm_fbf':FBQuantizeDataHandler,
        'art': FakeDataHandler,

        'gen_fb_mf':ModelFreeFeaGeneralizedEMHandler, # feature is model free emperical measure
        'gen_fb_mb':ModelBasedFeaGeneralizedEMHandler, # feature is model based emperical measure
        # 'expect':QuantizeGeneralizedEMHandler,
        }

from .Data import *
data_map = {
        'fs': MEM_FS,
        'pcap2netflow': MEM_Pcap2netflow,
        'flow_exporter': MEM_FlowExporter,
        'xflow': MEM_Xflow,
        'Sperotto': SperottoIPOM,
        'pt': PT_Data,
        }

def print_detector_help(type_):
    """print help message of detector with `type_`
    """
    detector = detector_map[ type_ ]({})
    detector.set_args(['-h'])

def detect(f_name, desc, res_args=[], real_time_logger=None):
    """An function for convenience
    - *f_name* the name or a list of name for the flow file.
    - *desc* is a parameter dictionary
    """
    # win_size = desc['win_size']
    # fea_option = desc['fea_option']
    data_file = data_map[ desc['data_type'] ](f_name)
    data_handler = data_handler_handle_map[desc['method']](data_file, desc)
    # data_handler = data_handler_handle_map[desc['detector_type']](data_file, fea_option)

    detector = detector_map[ desc['method'] ](desc)
    detector.set_args(res_args)
    # set real-time logger
    if real_time_logger:
        detector.real_time_logger = real_time_logger

    rdn = desc.get('ref_data') # reference data name
    if rdn:
        ref_data_file = data_map[ desc['data_type'] ](rdn)
        rdh = data_handler_handle_map[desc['method']](ref_data_file, desc) #reference data handler
        detector.detect(data_handler, rdh)
    else:
        detector.detect(data_handler)
        # detector.detect(data_handler, data_handler)

    return detector

def detector_plot_dump(data_name, type_, desc, *args, **kwargs):
    """don't actually detect, only plot precalculated data
    """
    detector = detector_map[type_](desc)
    detector.set_args([])
    detector.plot_dump(data_name, *args, **kwargs)

def _test_detect():
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
    _test_detect()
