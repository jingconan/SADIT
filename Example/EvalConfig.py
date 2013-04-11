# EXPORT_ABNORMAL_FLOW = True
# EXPORT_ABNORMAL_FLOW = False
# EXPORT_ABNORMAL_FLOW_PARA_FILE = ROOT + '/Share/ano_flow_para.txt'
# EXPORT_ABNORMAL_FLOW_PARA_FILE = ROOT + '/Share/ano_flow_para.txt'
# EXPORT_ABNORMAL_FLOW_FILE = ROOT + '/Simulator/abnormal_n0_flow.txt'
ROOT = '/home/wangjing/Dropbox/Research/sadit/'

#################################
##   Parameters For Detector  ###
#################################
# ANO_ANA_DATA_FILE = ROOT + '/Share/AnoAna.txt'
ANO_ANA_DATA_FILE = './Share/AnoAna.txt'
DETECTOR_DESC = dict(
        method = 'mfmb',
        data = './Simulator/n0_flow.txt',
        interval=20,
        # win_size=100,
        win_size=200,
        # win_size=20000,
        # win_size=200,
        win_type='time', # 'time'|'flow'
        # win_type='flow', # 'time'|'flow'
        fr_win_size=100, # window size for estimation of flow rate
        false_alarm_rate = 0.001,
        unified_nominal_pdf = False, # used in sensitivities analysis
        # discrete_level = DISCRETE_LEVEL,
        # cluster_number = CLUSTER_NUMBER,
        fea_option = {'dist_to_center':2, 'flow_size':2, 'cluster':3},
        # fea_option = {'dist_to_center':3, 'flow_size':2, 'cluster':3},
        # fea_option = {'dist_to_center':2, 'flow_size':2, 'cluster':2},
        # fea_option = {'dist_to_center':1, 'flow_size':3, 'cluster':1},
        # fea_option = {'dist_to_center':2, 'octets':2, 'cluster':2},
        # fea_option = {'dist_to_center':2, 'flow_size':2, 'cluster':1},
        ano_ana_data_file = ANO_ANA_DATA_FILE,
        # normal_rg = [0, 1000],
        # normal_rg = [0, 1000],
        normal_rg = None,
        # normal_rg = [0, 300],
        # normal_rg = [0, 4000],
        # normal_rg = [0, float('inf')],
        detector_type = 'mfmb',
        max_detect_num = None,
        # max_detect_num = 10,
        # max_detect_num = 20,
        # max_detect_num = 100,
        # data_handler = 'fs',
        data_type = 'fs',
        pic_show = True,
        pic_name = './res2.eps',
        # data_handler = 'fs_deprec',

        export_flows = None,
        csv = None,

        #### only for SVM approach #####
        # gamma = 0.01,

        #### only for Generalized Emperical Measure #####
        small_win_size = 1,
        # small_win_size = 1000,
        g_quan_N = 3,

        ab_win_num = 10,
        max_search_mb_states = 144,
        max_search_mf_states = 12,
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
