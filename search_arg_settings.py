"""
Settings for searching best arguments.
if you specify some attributes to be list. all combination of possible
values of those parameters will be exectued and result will be stored
in ./res/ folder
"""
desc = dict(
    # interval=[20, 30],
    interval=5,
    # win_size=[200, 300],
    win_size=200,
    win_type='time', # 'time'|'flow'
    fr_win_size=100, # window size for estimation of flow rate
    false_alarm_rate = 0.001,
    unified_nominal_pdf = False, # used in sensitivities analysis
    fea_option = {
        'dist_to_center':2,
        'flow_size':2,
        'cluster':[2, 4, 6]
        },
    normal_rg = None,
    detector_type = 'mfmb',
    max_detect_num = 200,
    # data_handler = 'fs_deprec',
    # flow_file = '../Simulator/n0_flow.txt',
    data_handler = 'xflow',
    flow_file = '../../CyberData/20030902.07.flow.txt',
)
