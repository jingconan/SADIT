# DEFAULT_PROFILE = (0, 8000, 1)
DEFAULT_PROFILE = (0, 2000, 1)
# Specify the link property
link_attr = {'weight':'10', 'capacity':'10000000', 'delay':'0.01'} # link Attribute


#################################
##   Parameter For Normal Case ##
#################################

GENERATOR = 'HARPOON'
# HARPOON = (4e5, 100, 0.5) # (fSize_mean, fSize_var, lambda)
HARPOON = ('4e5', '100', '0.5')
# HARPOON = ('randint(4e3, 4e5)', '1000', '0.5')
# JING = ''

#############################
##   Parameter For Markov  ##
#############################
MARKOV_PARA = [( 'normal(4e5,10)', 'exponential(3)'), # flow size for high state , interarrival time for high state
        ('normal(4e5,10)', 'exponential(0.3)')] # low state
MARKOV_P = [(0, 1), (0, 1)] # NORMAL
MARKOV_INTERVAL = 0.1



#############################
##   Parameter For Anomaly ##
#############################
# ANOMALY_TIME = (3000, 3500) # (startTime, endTime)
# ANOMALY_TIME = (2000, 3000) # (startTime, endTime)
# ANOMALY_TIME = (600, 800) # (startTime, endTime)
ANOMALY_TIME = (1200, 1400) # (startTime, endTime)
# ANOMALY_TIME = (200, 300) # (startTime, endTime)
# ANOMALY_TIME = (1000, 1300) # (startTime, endTime)
# ANOMALY_TIME = (6000, 7000) # (startTime, endTime)

##### Atypical User Anomaly #####
# ANOMALY_TYPE = 'ATYPICAL_USER'

### FLOW_RATE Anomaly ####
ANOMALY_TYPE = 'FLOW_RATE'
FLOW_RATE = 6
# FLOW_RATE = 0.1

### FLOW_SIZE Anomaly ####
# ANOMALY_TYPE = 'FLOW_SIZE'
# FLOW_SIZE_MEAN = 3 # The ratio between abnormal and normal flow size mean
# FLOW_SIZE_MEAN = 0.1 # The ratio between abnormal and normal flow size mean
# FLOW_SIZE_MEAN = 1e6
# FLOW_SIZE_MEAN = 1e3
FLOW_SIZE_VAR = 100 # Absolute FLOW_SIZE_VARIANCE
# FLOW_SIZE_VAR = 400

### FLOW_DURATION Anomaly ####
# FLOW_DURATION = 0.1

### Markovian Anomaly  #####
# ANOMALY_TYPE = 'MARKOV_TRAN_PROB'
# ABNORMAL_TRAN_PROB= [0.5, 0.5] # [p12, p21]


#############################
## Sensitivity Analysis    ##
#############################
FLOW_RATE_RANGE = [4, 6, 8]


### ROOT is the root directory for you directory, be aware to change this before you try to run the code
# ROOT = '/Users/jingwang/Dropbox/Research/CyberSecurity/code/newanomalydetector/neat_code'
#ROOT = '/Users/jingwang/Dropbox/Research/Cybersecurity/code/newanomalydetector/neat_code_sens'
# ROOT = '/home/wangjing/Dropbox/Research/CyberSecurity/code/newanomalydetector/neat_code_sens'

ROOT = '/home/wangjing/Documents/OpenSource/sadit-sphinx'

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
# DISCRETE_LEVEL = [2, 2]
DISCRETE_LEVEL = [2, 2, 2]
# DISCRETE_LEVEL = [2, 2, 2, 2]
CLUSTER_NUMBER = 2


LOAD_FEATURE = """
feaVec = [
         flowSize,
         # dur,
         flowRate,
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


FLOW_SIZE_TEST_RANGE = [1.5, 2.0, 2.5, 3.0]
# FLOW_SIZE_TEST_RANGE = [2]
# FLOW_RATE_TEST_RANGE = [1.5, 2.0, 2.5, 3.0]


ANO_ANA_DATA_FILE = ROOT + '/Share/AnoAna.txt'
ANO_CONF_PARA_FILE = ROOT + '/Share/AnoPara.txt'


DERI_TEST_THRESHOLD = 0.1
# DERI_TEST_THRESHOLD = 1


# ANOMALY_TYPE_DETECT_INDI = 'derivative'
# MODEL_FREE_DERI_DESCENDING_FIG = ROOT + '/res/mf-descending-deri.eps'
# MODEL_BASE_DERI_DESCENDING_FIG = ROOT + '/res/mb-descending-deri.eps'

ANOMALY_TYPE_DETECT_INDI = 'component'
MODEL_FREE_DERI_DESCENDING_FIG = ROOT + '/res/mf-descending-comp.eps'
MODEL_BASE_DERI_DESCENDING_FIG = ROOT + '/res/mb-descending-comp.eps'
