""" parameter required
sim_t
"""
#################################
##   Parameter For Normal Case ##
#################################
# sim_t = 8000
start = 0
DEFAULT_PROFILE = ((sim_t,),(1,))

# gen_desc = {'TYPE':'harpoon', 'flow_size_mean':'4e5', 'flow_size_var':'100', 'flow_arrival_rate':'0.5'}
gen_desc = {'TYPE':'harpoon', 'flow_size_mean':'4e3', 'flow_size_var':'100', 'flow_arrival_rate':'1'}
NORM_DESC = dict(
        TYPE = 'NORMAl',
        start = '0',
        node_para = {'states':[gen_desc]},
        profile = DEFAULT_PROFILE,
        )

# ANOMALY_TIME = (1200, 1400)
# ANO_DESC = {'anoType':'TARGET_ONE_SERVER',
ANO_DESC = {
        'anoType':'anomaly',
        'ano_node_seq':2,
        'T':(2000, 3000),
        # 'change':{'flow_size_mean':6},
        'change':{'flow_arrival_rate':6},
        'srv_id':0,
        }

ANO_LIST = [ANO_DESC]
