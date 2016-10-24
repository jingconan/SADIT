# ROOT = '/home/wangjing/Dropbox/Research/sadit/'
# ROOT = '/home/jzh/Dropbox/Git/sadit/'

import os
ROOT = os.environ['SADIT_ROOT']

#################################
##   Parameters For Detector  ###
#################################
ANO_ANA_DATA_FILE = './Share/AnoAna.txt'
DETECTOR_DESC = dict(
        # method = 'mfmb',
        # data = './Simulator/n0_flow.txt',
        # file_type = 'SQL',
        interval=2000,
        win_size=2000,
        win_type='time', # 'time'|'flow'
        # win_type='flow', # 'time'|'flow'
        fr_win_size=100, # window size for estimation of flow rate
        false_alarm_rate = 0.001,
        unified_nominal_pdf = False, # used in sensitivities analysis
        ano_ana_data_file = ANO_ANA_DATA_FILE,
        normal_rg = None,
        detector_type = 'mfmb',
        max_detect_num = None,
        data_type = 'fs',
        pic_show = True,
        pic_name = './res2.eps',

        export_flows = None,
        csv = None,

        #### only for SVM approach #####
        # gamma = 0.01,

        ##### For Batch Method #######
        batch_var = ['fea_option.dist_to_center'],
        #fea_option = {'dist_to_center':[1, 2, 3], 'flow_size':3, 'cluster':1},
	fea_option = {'cluster':(2, [0, 20]), 'dist_to_center':(1, [0, 1000]), 'flow_size':(2, [0, 50000])},
        res_folder = './res/res_batch_test/',
        data = './Simulator/n0_flow.txt',
        method = 'mfmb',
        entropy_threshold = None,
        ab_win_portion = None,
        ab_win_num = 10,
        ident = {
            'mf': {
                'ident_type': 'ComponentFlowStateIdent',
                'portion': None,
                'ab_states_num': 1,
                },

            'mb': {

                # 'ident_type': None,
                'ident_type': 'ComponentFlowPairIdent',
                'portion': None,
                'ab_states_num': 1,
                },
            },

        )
