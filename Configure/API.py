from Network import Network
from Anomaly import AtypicalUserAnomaly, Anomaly, TargetOneServer
from MarkovAnomaly import MarkovAnomaly
from MVAnomaly import MVAnomaly
##################################
###  Interface          #######
##################################
ano_map = {
        # 'ATYPICAL_USER':AtypicalUser,
        'atypical_user':AtypicalUserAnomaly,
        'anomaly':Anomaly,
        'flow_arrival_rate':Anomaly,
        'flow_size_mean':Anomaly,
        'flow_size_var':Anomaly,
        'target_one_server':TargetOneServer,
        'markov_anomaly':MarkovAnomaly,
        'mv_anomaly':MVAnomaly,
        }

def gen_anomaly_dot(ano_list, netDesc, normalDesc, outputFileName):
    net = Network()
    net.init(netDesc, normalDesc)
    for ano_desc in ano_list:
        ano_type = ano_desc['anoType'].lower()
        AnoClass = ano_map[ano_type]
        A = AnoClass(ano_desc)
        net.InjectAnomaly( A )

    net.write(outputFileName)

