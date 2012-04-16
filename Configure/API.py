from Network import *
from anomaly import *
from MarkovAnomaly import *
##################################
###  Interface          #######
##################################
ano_map = {
        # 'ATYPICAL_USER':AtypicalUser,
        'atypical_user':AtypicalUserAnomaly,
        'flow_arrival_rate':Anomaly,
        'flow_size_mean':Anomaly,
        'flow_size_var':Anomaly,
        'target_one_server':TargetOneServer,
        'markov_anomaly':MarkovAnomaly,
        }

def GenAnomalyDot(ano_list, netDesc, normalDesc, outputFileName):
    net = Network()
    net.init(netDesc, normalDesc)
    for ano_desc in ano_list:
        ano_type = ano_desc['anoType'].lower()
        AnoClass = ano_map[ano_type]
        A = AnoClass(ano_desc)
        net.InjectAnomaly( A )

    net.write(outputFileName)

