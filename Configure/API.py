from __future__ import print_function, division, absolute_import
from .Network import Network
from .Anomaly import AtypicalUserAnomaly, Anomaly, TargetOneServer, AddModulatorAnomaly
from .MarkovAnomaly import MarkovAnomaly
from .MVAnomaly import MVAnomaly
##################################
###  Interface          #######
##################################
ano_map = {
        # 'ATYPICAL_USER':AtypicalUser,
        'atypical_user':AtypicalUserAnomaly,
        'add_mod':AddModulatorAnomaly,
        'anomaly':Anomaly,
        'flow_arrival_rate':Anomaly,
        'flow_size_mean':Anomaly,
        'flow_size_var':Anomaly,
        'target_one_server':TargetOneServer,
        'markov_anomaly':MarkovAnomaly,
        'mv_anomaly':MVAnomaly,
        }

def gen_dot(ano_list, net_desc, normal_desc, output_f_name):
    """  generate dot file for simulation

    Parameters
    ---------------
    ano_list : list of dictionary
        each element is a descriptor for an anomaly

    net_desc : dictionary
        descriptor for network

    normal_desc : dictionary
        descriptor for normal traffic

    output_f_name : str
        name for the output file

    Returns
    --------------
    None

    """
    net = Network()
    net.init(net_desc, normal_desc)
    for ano_desc in ano_list:
        ano_type = ano_desc['anoType'].lower()
        AnoClass = ano_map[ano_type]
        A = AnoClass(ano_desc)
        net.InjectAnomaly( A )

    net.write(output_f_name)

