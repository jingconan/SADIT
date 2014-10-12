# ROOT = '/home/wangjing/Dropbox/Research/sadit/'
ROOT = '/home/jzh/Dropbox/Git/sadit/'
DIR = '/home/jzh/Dropbox/SaditTest/Robust_Method/PaperSimulation/FlowSizeSlowDrift/'

import numpy as np
#################################
##   Parameters For Detector  ###
#################################
# import itertools
# ANO_ANA_DATA_FILE = ROOT + '/Share/AnoAna.txt'
ANO_ANA_DATA_FILE = './Share/AnoAna.txt'
DETECTOR_DESC = dict(
        # method = 'robust',
        # method = 'mfmb',
        comp_methods = ['robust', 'mfmb'],
        # data = DIR + 'n0_flow_50_anomalies.txt',
        # data = DIR + 'n0_flow_1_ano_200000_205000.txt',
        # data = DIR + 'n0_flow_reference.txt',
        # ref_data = DIR + 'n0_flow_reference.txt',
        data = DIR + 'n0_flow_1_ano_200000_205000.txt',
        ref_data = DIR + 'n0_flow_reference_steady_shift.txt',
        dump_folder = DIR + 'resCompOneAno/',
        # ref_data = DIR + 'n0_flow_50_anomalies.txt',
        normal_rg = None,
        # interval = 5000,
        interval = 1000,
        win_size=1000,
        win_type='time', # 'time'|'flow'
        fr_win_size=100, # window size for estimation of flow rate
        false_alarm_rate = 0.001,
        unified_nominal_pdf = False, # used in sensitivities analysis
        fea_option = {'dist_to_center':5, 'flow_size':10, 'cluster':1},
        # fea_option = {'dist_to_center':1, 'flow_size':2, 'cluster':1},
        ano_ana_data_file = ANO_ANA_DATA_FILE,
        max_detect_num = None,
        data_type = 'fs',
        pic_show = True,
        pic_name = './res2.eps',
        export_flows = None,
        csv = None,

        ####### Only for Robust approach #####
        register_info = {
            'FBAnoDetector' : {
                'type' : 'static',
                'para' : {
                    # ref_data = [DIR + 'n0_referece_normal.txt'],
                    'method' : ['mfmb'],

                    # 'normal_rg' : [100000, 500000],
                    # 'fea_option' : [
                        # {'dist_to_center':1, 'flow_size':2, 'cluster':1},
                        # {'dist_to_center':1, 'flow_size':3, 'cluster':1},
                        # {'dist_to_center':1, 'flow_size':4, 'cluster':1},
                        # {'dist_to_center':1, 'flow_size':5, 'cluster':1},
                        # ]
                    } #FIXME
                },
            # 'PeriodStaticDetector' : {
            #     'type' : 'static',
            #     'para' :  {
            #         'period':np.array([24]) * 3600,
            #         'start': np.sin(np.arange(0, 24*3600, 1000)),
            #         'delta_t':[1000, 2000, 3000],
            #         },
            #     },
            'SlowDriftStaticDetector' : {
                'type' : 'static',
                'para' : {
                    # 'start' : [0, 25000, 80000, 120000, 200000, 240000],
                    # 'delta_t' : [25000, 55000, 40000, 80000, 40000, 20000],
                    'start' : [0, 50000, 170000, 270000, 350000, 420000,
                        500000],
                    'delta_t' : [50000,  120000, 100000, 80000, 70000, 80000,
                        100000],
                    # 'start':np.arange(1, 168, 6) * 3600,
                    # 'start':np.linspace(0, 6e5, 20),
                    # 'start':np.arange(1, 6e5, 1.5*1e5),
                    # 'start':np.arange(1, 6e5, 1.5*1e5),
                    # 'delta_t':[1.5*1e5],
                    # 'delta_t':[1.5*1e5],
                    # 'start':[3e5],
                    # 'delta_t':[3e5]
                    },
                # 'ctype' : itertools.product,
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
