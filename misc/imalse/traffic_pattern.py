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
gen_desc = {'TYPE':'harpoon', 'flow_size_mean':'4e3', 'flow_size_var':'100', 'flow_arrival_rate':'0.5'}
NORM_DESC = dict(
        TYPE = 'NORMAl',
        start = '0',
        node_para = {'states':[gen_desc]},
        profile = DEFAULT_PROFILE,
        # there will be traffic from any combination of src_nodes
        # and dst_nodes
        # src_nodes = [0, 1, 2, 3, 4, 5, 7, 8, 9, 10, 11, 12, 13],
        src_nodes = [0, 1, 2, 3, 4, 5, 7, 8, 10, 11, 12, 13],
        dst_nodes = [0, 1, 2, 3, 4, 5, 7, 8, 10, 11, 12, 13],
        )

# ANOMALY_TIME = (1200, 1400)
# ANO_DESC = {'anoType':'TARGET_ONE_SERVER',
ANO_DESC = dict(
        # anoType = 'anomaly',
        anoType = 'add_mod',
        ano_node_seq = 9,
        T = (1000, 1300),
        gen_desc = gen_desc,
        dst_nodes = [1],
        # change = {'flow_size_mean':2},
        # change = {'flow_arrival_rate':3},
        # change = gen_desc,
        # change = {'flow_arrival_rate':6},
        # srv_id = 1,
        )

ANO_LIST = [ANO_DESC]
