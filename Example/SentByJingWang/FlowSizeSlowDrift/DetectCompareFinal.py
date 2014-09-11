# ROOT = '/home/wangjing/Dropbox/Research/sadit/'
ROOT = '/home/jzh/software/sadit/'


DIR = '/home/jzh/Research/CyberSecurity/Robust_Method/PaperSimulation/FlowSizeSlowDrift/'
import numpy as np
#################################
##   Parameters For Detector  ###
#################################
ANO_ANA_DATA_FILE = './Share/AnoAna.txt'
DETECTOR_DESC = dict(
        lamb = 0.7,
        ref_scheck = 'load',
        comp_methods = ['robust', 'mfmb'],
        data = DIR + 'n0_flow_reference_1_ano_steady_shift.txt',
        ref_data = DIR + 'n0_flow_reference_1_ano_steady_shift.txt',
        # ref_data = DIR + 'n0_flow_reference_steady_shift.txt',
        dump_folder = DIR + 'DetectCompareResult/',
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
            'FBAnoDetector' : {
                'type' : 'static',
                'para' : {
                    'method' : ['mfmb'],
                    } #FIXME
                },

            'SlowDriftStaticDetector' : {
                'type' : 'static',
                'para' : {
                    # 'start' : [0, 25000, 80000, 120000, 200000, 240000],
                    # 'delta_t' : [25000, 55000, 40000, 80000, 40000, 20000],
                    # 'start' : [0, 50000, 170000, 270000, 350000, 420000,
                    #     500000],
                    # 'delta_t' : [50000,  120000, 100000, 80000, 70000, 80000,
                    #     100000],
                    # 'start':np.arange(1, 168, 6) * 3600,
                    # 'start':np.linspace(0, 6e5, 20),
                    # 'start':np.arange(1, 6e5, 1.5*1e5),
                    'start':np.arange(1, 6e5, 5*1e4),
                    'delta_t':[5*1e4],
                    # 'delta_t':[1.5*1e5],
                    # 'start':[3e5],
                    # 'delta_t':[3e5]
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
