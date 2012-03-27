'''This file provides API for all three modules:
    1 Configure module,
    2 Simulator module,
    3 Detector module
'''
#########################################
####           Configure API          ###
#########################################
from Configure.anomaly import *
from Configure.MarkovAnomaly import *
from Detector.AnomalyAna import ModelFreeDetectAnoType, ModelBaseDetectAnoType,GetAnomalyType, ModelFreeHTest, ModelBaseHTest

def GlobalConfigure():
    '''Generate configuration file accroding to settings.py'''
    reload(settings)
    startTime, endTime = settings.ANOMALY_TIME
    outputFileName = settings.OUTPUT_DOT_FILE
    anoType = settings.ANOMALY_TYPE
    if anoType == 'ATYPICAL_USER':
        GenAtypicalUserAnomalyDot(startTime, endTime, outputFileName)
    elif anoType == 'FLOW_SIZE':
        GenFlowSizeAnomalyDot(startTime, endTime, settings.FLOW_SIZE_MEAN, settings.FLOW_SIZE_VAR, outputFileName)
    elif anoType == 'FLOW_RATE':
        print 'FLOW_RATE, ', settings.FLOW_RATE
        GenFlowRateAnomalyDot(startTime, endTime, settings.FLOW_RATE, outputFileName)
    elif anoType == 'MARKOV_TRAN_PROB':
        GenMarkovTranAnomalyDot(startTime ,endTime,
                settings.ABNORMAL_TRAN_PROB[0],settings.ABNORMAL_TRAN_PROB[1], outputFileName)
    else:
        raise ValueError('unknow anomaly type')


#########################################
####          Simulator API          ###
#########################################
from os import chdir as cd
from os import system as sh
def Simulate():
    simTime = settings.DEFAULT_PROFILE[1]
    dotPath = settings.OUTPUT_DOT_FILE

    cd('./Simulator')
    sh( './fs.py %s -t %d' %(dotPath, simTime) )
    cd('..')




#########################################
####          Simulator API          ###
#########################################
from Detector.Detector import Compare as GlobalDetect
from Detector.Detector import GenNominalPDF

def GlobalGenerateNominalPDF():
    reload(settings)
    GlobalConfigure()
    Simulate()
    print 'Simulate Done'
    GenNominalPDF(settings.OUTPUT_FLOW_FILE,
            settings.DISCRETE_LEVEL + [settings.CLUSTER_NUMBER],
            True)
