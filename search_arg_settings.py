"""
Settings for searching best arguments.
if you specify some attributes to be list. all combination of possible
values of those parameters will be exectued and result will be stored
in ./res/ folder
"""
desc_2003 = dict(
    # interval=[20, 30],
    interval=1,
    # win_size=[200, 300],
    # win_size=200,
    win_size=2,
    win_type='time', # 'time'|'flow'
    fr_win_size=100, # window size for estimation of flow rate
    false_alarm_rate = 0.001,
    entropy_threshold = None,
    # entropy_threshold = 0.1,
    ab_win_portion = None,
    # ab_win_num = None,
    # ab_win_num = [1, 5, 10],
    ab_win_num = 5,
    unified_nominal_pdf = False, # used in sensitivities analysis
    fea_option = {
        'dist_to_center':2,
        'flow_size':2,
        'cluster':[4, 6]
        },
    normal_rg = None,
    detector_type = 'mfmb',
    # max_detect_num = 200,
    # max_detect_num = 20,
    # max_detect_num = None,
    max_detect_num = 10,
    # data_handler = 'fs_deprec',
    # flow_file = '../Simulator/n0_flow.txt',
    data_handler = 'xflow',
    flow_file = '../../CyberData/20030902.07.flow.txt',
    # flow_file = '../../CyberData/back_20030902.07.flow.txt',
    ident = {
        'mf': {
            'ident_type': 'ComponentFlowStateIdent',
            'portion': None,
            'num': 1,
            },
        'mb': {

            # 'ident_type': None,
            'ident_type': 'ComponentFlowPairIdent',
            'portion': None,
            'num': 1,
            },
        }
)

desc_2007 = dict(
    # interval=[20, 30],
    interval=1000,
    # win_size=[200, 300],
    # win_size=200,
    win_size=2000,
    win_type='time', # 'time'|'flow'
    fr_win_size=100, # window size for estimation of flow rate
    false_alarm_rate = 0.001,
    entropy_threshold = None,
    # entropy_threshold = 0.1,
    ab_win_portion = None,
    # ab_win_num = None,
    # ab_win_num = 10,
    ab_win_num = [1, 5, 10],
    unified_nominal_pdf = False, # used in sensitivities analysis
    fea_option = {
        # 'dist_to_center':[2, 4, 6],
        # 'flow_size':[2, 4, 6],
        # 'cluster':[2, 4, 6]
        'dist_to_center': 4,
        'flow_size':4,
        'cluster':4
        },
    normal_rg = None,
    detector_type = 'mfmb',
    max_detect_num = None,
    data_handler = 'xflow',
    flow_file = '../../CyberData/20070501.18.flow.txt',
)

# desc = desc_2007
desc = desc_2003
