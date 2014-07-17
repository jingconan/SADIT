from .GUITopoSim import GUITopoSim
from .Sim import Sim
try:
    from Detector.gad.Experiment import *
except:
    print '[warning]: experiments in Detector submodule cannot be initialized'
    pass
