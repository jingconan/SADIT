# ROOT = '/home/wangjing/Dropbox/Research/sadit/'
ROOT = '/home/jzh/software/sadit/'

DIR = \
'/home/jzh/Research/CyberSecurity/Robust_Method/PaperSimulation/FlowSizeArrivalBothPeriod/'


import numpy as np
#################################
##   Parameters For Detector  ###
#################################
ANO_ANA_DATA_FILE = './Share/AnoAna.txt'
DETECTOR_DESC = dict(
        lamb = 5,
        ref_scheck = 'dump',
        comp_methods = ['robust'],
        data = DIR + 'n0_flow_reference.txt',
        ref_data = DIR + 'n0_flow_reference.txt',
        dump_folder = DIR + 'SelfCheck/',
        normal_rg = None,
        interval = 1000,
        win_size=1000,
        win_type='time', # 'time'|'flow'
        fr_win_size=100, # window size for estimation of flow rate
        false_alarm_rate = 0.001,
        unified_nominal_pdf = False, # used in sensitivities analysis
        fea_option = {'dist_to_center':5, 'flow_size':8, 'cluster':1},
        ano_ana_data_file = ANO_ANA_DATA_FILE,
        max_detect_num = None,
        data_type = 'fs',
        pic_show = True,
        pic_name = './res2.eps',
        export_flows = None,
        csv = None,

        ####### Only for Robust approach #####
        register_info = {
            'PeriodStaticDetector' : {
                'type' : 'static',
                'para' :  {
                    # 'period':[24 * 3600] ,
                    # 'start': np.linspace(0, 12*3600, 7),
                    'period': np.linspace(24*3600, 1.5*24*3600, 4),
                    'start': np.linspace(0, 24 * 3600, 8),
                    'delta_t':[1000],
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
