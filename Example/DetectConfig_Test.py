import os
ROOT = os.environ['SADIT_ROOT']

#################################
##   Parameters For Detector  ###
#################################
ANO_ANA_DATA_FILE = './Share/AnoAna.txt'
DETECTOR_DESC = dict(
        interval=20,
        win_size=300,
        win_type='time', # 'time'|'flow'
        fr_win_size=100, # window size for estimation of flow rate
        false_alarm_rate = 0.00001,
        fea_option = {'dist_to_center':2, 'flow_size':2, 'cluster':3},
        ano_ana_data_file = ANO_ANA_DATA_FILE,
        normal_rg = None,
        max_detect_num = None,
        data_type = 'fs',
        pic_show = True,
        pic_name = './res.eps',

        export_flows = None,
        csv = None,
        )




