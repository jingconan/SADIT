from .GUITopoSim import GUITopoSim as guitoposim
from .Sim import Sim as sim
try:
    from Detector.gad.Experiment import *
except:
    print '[warning]: experiments in Detector submodule cannot be initialized'
    pass
