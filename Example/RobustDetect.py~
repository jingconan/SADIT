# ROOT = '/home/wangjing/Dropbox/Research/sadit/'
ROOT = '/home/jzh/software/sadit/'

import numpy as np
#################################
##   Parameters For Detector  ###
#################################
# ANO_ANA_DATA_FILE = ROOT + '/Share/AnoAna.txt'
ANO_ANA_DATA_FILE = './Share/AnoAna.txt'
DETECTOR_DESC = dict(
        method = 'robust',
        # method = 'mfmb',
        # data = './Simulator/n0_flow.txt',
        ref_scheck = 'dump',
        interval=100,
        win_size=100,
        win_type='time', # 'time'|'flow'
        fr_win_size=100, # window size for estimation of flow rate
        false_alarm_rate = 0.001,
        unified_nominal_pdf = False, # used in sensitivities analysis
        fea_option = {'dist_to_center':2, 'flow_size':2, 'cluster':2},
        # fea_option = {'dist_to_center':1, 'flow_size':2, 'cluster':1},
        dump_folder = ROOT + 'res/',
        ano_ana_data_file = ANO_ANA_DATA_FILE,
        normal_rg = None,
        ref_data = ROOT + 'Simulator/n0_flow.txt',
        # normal_rg = None,
        detector_type = 'mfmb',
        max_detect_num = None,
        data_type = 'fs',
        pic_show = True,
        pic_name = './res2.eps',
        # data_handler = 'fs_deprec',

        export_flows = None,
        csv = None,

        ####### Only for Robust approach #####
        register_info = {
            'FBAnoDetector' : {
                'type' : 'static',
                'para' : {
                    'normal_rg' : None,
                    },
                'para_type' : 'product',
                },
            'PeriodStaticDetector' : {
                'type' : 'static',
                'para' :  {
                    'period':[10, 100, 1000],
                    'start': [30],
                    'delta_t':[1000],
                    },
                'para_type' : 'product',
                },
            'SlowDriftStaticDetector' : {
                'type' : 'static',
                'para' : {
                    # 'start':np.arange(1, 168, 6) * 3600,
                    'start':np.linspace(1, 3000, 3),
                    'delta_t':[100, 300]
                    },
                'para_type' : 'product',
                },
            },

        #### only for SVM approach #####
        # gamma = 0.01,

        #### only for Generalized Emperical Measure #####
        small_win_size = 1,
        # small_win_size = 1000,
        g_quan_N = 3,
        )
# when using different data_hanlder, you will have different set of avaliable options for fea_option.

FLOW_RATE_ESTIMATE_WINDOW = 100 #only for test

FALSE_ALARM_RATE = 0.001 # false alarm rate
NominalPDFFile = ROOT + '/Share/nominal.p'
UNIFIED_NOMINAL_PDF = False


#########################################
### Parameters for Derivative Test  ####
#########################################
DERI_TEST_THRESHOLD = 0.1
# DERI_TEST_THRESHOLD = 1

# ANOMALY_TYPE_DETECT_INDI = 'derivative'
# MODEL_FREE_DERI_DESCENDING_FIG = ROOT + '/res/mf-descending-deri.eps'
# MODEL_BASE_DERI_DESCENDING_FIG = ROOT + '/res/mb-descending-deri.eps'

ANOMALY_TYPE_DETECT_INDI = 'component'
MODEL_FREE_DERI_DESCENDING_FIG = ROOT + '/res/mf-descending-comp.eps'
MODEL_BASE_DERI_DESCENDING_FIG = ROOT + '/res/mb-descending-comp.eps'
