### ROOT is the root directory for you directory, be aware to change this before you try to run the code
ROOT = '/Users/wangjing/Dropbox/Research/CyberSecurity/code/sadit'
ROOT = '/home/wangjing/Dropbox/Research/CyberSecurity/code/sadit'

#################################
##   Network Topology ##
#################################
# Specify the link property
link_attr = {'weight':'10', 'capacity':'10000000', 'delay':'0.01'} # link Attribute
from numpy import zeros, array
# topo = array(
        # [[0, 0, 0],
        # [1, 0, 0],
        # [0, 0, 1]]
        # )
# Generate Star topology
g_size = 10
srv_node_list = [0, 1]
# srv_node_list = [0]
topo = zeros([g_size, g_size])
for i in xrange(g_size):
    if i in srv_node_list:
        continue
    topo[i, srv_node_list] = 1

# topo[3, 5] = 1
# topo[4, 6] = 1

NET_DESC = dict(
        topo=topo,
        size=topo.shape[0],
        srv_list=srv_node_list,
        link_attr=link_attr,
        )

#################################
##   Parameter For Normal Case ##
#################################
# DEFAULT_PROFILE = (0, 8000, 1)
sim_t = 2000
start = 0
DEFAULT_PROFILE = ((sim_t,),(1,))

NORM_DESC = dict(
        TYPE = 'NORMAl',
        start = '0',
        gen_desc = {'TYPE':'harpoon', 'flow_size_mean':'4e5', 'flow_size_var':'100', 'flow_arrival_rate':'0.5'},
        profile = DEFAULT_PROFILE,
        )

#######################################
##   Parameter For Markov normal case ##
#######################################
MARKOV_PARA = [( 'normal(4e5,10)', 'exponential(3)'), # flow size for high state , interarrival time for high state
        ('normal(4e5,10)', 'exponential(0.3)')] # low state
MARKOV_P = [(0, 1), (0, 1)] # NORMAL
MARKOV_INTERVAL = 0.1

#############################
##   Parameter For Anomaly ##
#############################
## Anomaly Description for Flow Rate type of anomaly
ANOMALY_TIME = (1200, 1400) # for detector
ANO_DESC = {'anoType':'FLOW_ARRIVAL_RATE',
        'ano_node_seq':2,
        'T':(1200, 1400),
        'ratio':6,
        }
# add normal to every node except for servers
import copy
ANO_LIST = []
for i in xrange(g_size):
    if i in srv_node_list:
        continue
    ad = copy.deepcopy(ANO_DESC)
    ad['ano_node_seq'] = i
    ANO_LIST.append(ad)
# ANO_LIST = [ANO_DESC]

# EXPORT_ABNORMAL_FLOW = True
EXPORT_ABNORMAL_FLOW = False

## Anomaly Description for Flow Size type of anomaly
# MEAN is the ratio between abnormal and normal flow size mean
# VAR is the absolute value of variance for the anomaly.
# ANO_DESC = {'anoType':'FLOW_SIZE',
        # 'T':(1200, 1400),
        # 'MEAN_RATIO':3,
        # 'VAR':100,
        # }

## Anomaly Description for Markov type of anomaly
# ANO_DESC = {'anoType':'MARKOV_TRAN_PROB',
        # 'T':(1200, 1400),
        # 'ABNORMAL_TRAN_PROB':[0.5, 0.5], # [p12, p21]
        # }



#############################
## Sensitivity Analysis    ##
#############################
FLOW_RATE_RANGE = [4, 6, 8]
FLOW_SIZE_TEST_RANGE = [1.5, 2.0, 2.5, 3.0]
# FLOW_SIZE_TEST_RANGE = [2]
# FLOW_RATE_TEST_RANGE = [1.5, 2.0, 2.5, 3.0]





# The path for output of configure
OUTPUT_DOT_FILE = ROOT + '/Share/conf.dot'

# THe path for flow data
OUTPUT_FLOW_FILE = ROOT + '/Simulator/n0_flow.txt'

#
ABNORMAL_USER_IP_FILE = ROOT + '/Share/abnormal_user_IP.txt'
ATYPICAL_IP_FILE = ROOT + '/Share/atypical_IP.txt'

IPS_FILE = ROOT + '/Configure/ips.txt'

#############################
##   Parameters For Detector ##
#############################
# DETECTOR_WINDOW_SIZE = 200
DETECTOR_INTERVAL = 10
DETECTOR_WINDOW_SIZE = 150
# WINDOW_TYPE = 'FLOW'
WINDOW_TYPE = 'TIME'
DETECTOR_PREFIX = 'markov'
FLOW_RATE_ESTIMATE_WINDOW = 100

# the state sequence
#    m_list = [gc[i] + gd[i]*K + gf[i]*K*ND for i in xrange(fl)]
#    CLUSTER_NUMBER determine the last dimension, distance to center determines
#    the second, flow size determine the first dimensition
#    index = [gc[i] + gd[i]*K + gf[i]*K*ND for i in xrange(fl)
# DISCRETE_LEVEL = (4, 4)
DISCRETE_LEVEL = [2, 2]
# DISCRETE_LEVEL = [2, 2, 2]
# DISCRETE_LEVEL = [2, 2, 2, 2]
CLUSTER_NUMBER = 2


LOAD_FEATURE = """
feaVec = [
         flowSize,
         # dur,
         # flowRate,
         distToCenter,
         cluster]"""

# LOAD_FEATURE = """feaVec = [flowSize, distToCenter, cluster]"""


FALSE_ALARM_RATE = 0.001 # false alarm rate

NominalPDFFile = ROOT + '/Share/nominal.p'
UNIFIED_NOMINAL_PDF = False


#####################################
###    Parameters for Analyzing Derivative  ###
#####################################
DERIVATIVE_FIGURE_DIR = ROOT + '/res/Derivative/'
PLOT_DERIVATIVE = False
# PLOT_DERIVATIVE = True
MODEL_BASE_DERI_DUMP_FILE = ROOT + '/Detector/model-base-deri.p'
MODEL_FREE_DERI_DUMP_FILE = ROOT + '/Detector/model-free-deri.p'

#############################################
###    Parameters for SVM Type Detection  ###
#############################################
ANOMALY_TYPE_SELECTION_SET = ['FLOW_SIZE', 'FLOW_RATE', 'ATYPICAL_USER']
# ANOMALY_TYPE_SELECTION_SET = ['FLOW_SIZE']
DEGREE_SELECTION_SET = ['increase', 'decrease']
TEST_NUM = 20
SVM_MODEL_FREE_DATA_FILE = ROOT + '/Share/SVM/modelfree'
SVM_MODEL_BASE_DATA_FILE = ROOT + '/Share/SVM/modelbase'
SVM_OUTPUT_FILE = ROOT + '/Share/SVM/a.out'
LIB_SVM_ROOT = ROOT + '/libsvm-3.11'
SVM_TRAIN_EXE = LIB_SVM_ROOT + '/svm-train'
SVM_PREDICT_EXE = LIB_SVM_ROOT + '/svm-predict'
# SVM_EASY_EXE = 'python ' + ROOT + '/tools/easy.py'
import os
def SVM_EASY_EXE(trainFile, testFile, outFile = 'a.out'):
    os.chdir(LIB_SVM_ROOT + '/tools')
    os.system('python easy.py ' + trainFile + ' ' + testFile + ' >' + outFile)

CROSS_VALIDATION_RATIO = 0.8



ANO_ANA_DATA_FILE = ROOT + '/Share/AnoAna.txt'
ANO_CONF_PARA_FILE = ROOT + '/Share/AnoPara.txt'


#########################################
### Parameters for Derivative Test  ####
#########################################
DERI_TEST_THRESHOLD = 0.1
# DERI_TEST_THRESHOLD = 1

# ANOMALY_TYPE_DETECT_INDI = 'derivative'
# MODEL_FREE_DERI_DESCENDING_FIG = ROOT + '/res/mf-descending-deri.eps'
# MODEL_BASE_DERI_DESCENDING_FIG = ROOT + '/res/mb-descending-deri.eps'

ANOMALY_TYPE_DETECT_INDI = 'component'
MODEL_FREE_DERI_DESCENDING_FIG = ROOT + '/res/mf-descending-comp.eps'
MODEL_BASE_DERI_DESCENDING_FIG = ROOT + '/res/mb-descending-comp.eps'
