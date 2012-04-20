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
from os import chdir as cd
from os import system as sh
from Detector.DetectorLib import compare as GlobalDetect
from Detector.DetectorLib import gen_norminal_pdf

from Detector.MSDetector import Detect as MSDetect
#########################################
####          Simulator API          ###
#########################################
def Simulate():
    simTime = settings.sim_t
    dotPath = settings.OUTPUT_DOT_FILE

    cd('./Simulator')
    sh( './fs.py %s -t %d' %(dotPath, simTime) )
    cd('..')




#########################################
####          Simulator API          ###
#########################################

def GlobalGenerateNominalPDF():
    reload(settings)
    GlobalConfigure()
    Simulate()
    print 'Simulate Done'
    gen_norminal_pdf(settings.OUTPUT_FLOW_FILE,
            settings.DISCRETE_LEVEL + [settings.CLUSTER_NUMBER],
            True)

