DEFAULT_PROFILE = (0, 8000, 1)

GENERATOR = 'HARPOON'
HARPOON = (4e5, 1, 0.5)

JING = ''

# Specify the link property
link_attr = {'weight':'10', 'capacity':'10000000', 'delay':'0.01'} # link Attribute

#############################
##   Parameter For Markov  ##
#############################
MARKOV_PARA = [( 'normal(4e5,10)', 'exponential(3)'), # flow size for high state , interarrival time for high state
                 ('normal(4e5,10)', 'exponential(0.3)')] # low state
MARKOV_P = [(0, 1), (0, 1)] # NORMAL
MARKOV_INTERVAL = 0.1

# Abnormal Transition Probability
TRAN_PROB = [(0.1, 0.9), (0.3, 0.7)]


#############################
##   Parameter For Anomaly ##
#############################
ANOMALY_TYPE = 'ATYPICAL_USER'
ANOMALY_TIME = (2000, 3000) # (startTime, endTime)
FLOW_RATE = 1
FLOW_DURATION = 0.1
FLOW_SIZE_MEAN = 4e4
FLOW_SIZE_VAR = 400

ROOT = '/Users/jingwang/Dropbox/Research/CyberSecurity/code/newanomalydetector/neat_code'

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
DETECTOR_WINDOW_SIZE = 200
DETECTOR_PREFIX = 'markov'
DISCRETE_LEVEL = (4, 4)
CLUSTER_NUMBER = 1


NominalPDFFile = ROOT + '/Share/nominal.p'
