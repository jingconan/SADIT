'''This file provides API for all three modules:
    1 Configure module,
    2 Simulator module,
    3 Detector module
'''
#########################################
####           Configure API          ###
#########################################
# from Configure.anomaly import *
# from Configure.MarkovAnomaly import *
from Configure import *

from Detector.AnomalyAna import ModelFreeDetectAnoType, ModelBaseDetectAnoType,GetAnomalyType, ModelFreeHTest, ModelBaseHTest

#########################################
####          Simulator API          ###
#########################################
from os import chdir as cd
from os import system as sh
def Simulate():
    simTime = settings.sim_t
    dotPath = settings.OUTPUT_DOT_FILE

    cd('./Simulator')
    sh( './fs.py %s -t %d' %(dotPath, simTime) )
    cd('..')




#########################################
####          Simulator API          ###
#########################################
from Detector.Detector import compare as GlobalDetect
from Detector.Detector import gen_norminal_pdf

def GlobalGenerateNominalPDF():
    reload(settings)
    GlobalConfigure()
    Simulate()
    print 'Simulate Done'
    gen_norminal_pdf(settings.OUTPUT_FLOW_FILE,
            settings.DISCRETE_LEVEL + [settings.CLUSTER_NUMBER],
            True)

from Detector.MSDetector import Detect as MSDetect
