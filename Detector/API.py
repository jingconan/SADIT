from Detector_basic import ModelFreeAnoDetector, ModelBaseAnoDetector, FBAnoDetector
detector_map = {
        'mf': ModelFreeAnoDetector,
        'mb': ModelBaseAnoDetector,
        'mfmb': FBAnoDetector,
        }


from DataHandler import HardDiskFileHandler, HardDiskFileHandler_pcap2netflow, SQLDataFileHandler_SperottoIPOM2009, DataFile
from DataHandler_xflow import HardDiskFileHandler_xflow
data_handler_handle_map = {
        'fs': HardDiskFileHandler,
        'fs_deprec': DataFile,
        'pcap2netflow': HardDiskFileHandler_pcap2netflow,
        'SperottoIPOM2009': SQLDataFileHandler_SperottoIPOM2009,
        'xflow': HardDiskFileHandler_xflow,
        }

# def detect(f_name, win_size, fea_option, detector_type, detector_desc):
def detect(f_name, desc):
    """An function for convenience
    - *f_name* the name or a list of name for the flow file.
    - *win_size* the window size
    - *fea_option*

    """
    win_size = desc['win_size']
    fea_option = desc['fea_option']
    data_file = data_handler_handle_map[ desc['data_handler'] ](f_name, win_size, fea_option)
    detector = detector_map[ desc['detector_type'] ](desc)
    detector.detect(data_file)
    return detector
# type_detector = ModelFreeAnoTypeTest(detect, 3000, settings.ANO_DESC['T'])
    # type_detector.detect_ano_type()

    # type_detector = ModelBaseAnoTypeTest(detect, 3000, settings.ANO_DESC['T'])
    # type_detector.detect_ano_type()

    # import pdb;pdb.set_trace()
    # detect.plot_entropy()

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

# def standalone_detect(file_name):
#     from settings import DETECTOR_DESC as desc
#     detector = detect(file_name, desc)

#     detector.plot_entropy()

if __name__ == "__main__":
    test_detect()
