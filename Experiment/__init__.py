from .GUITopoSim import GUITopoSim as guitoposim
from .Sim import Sim as sim
try:
    from Detector.gad.Experiment import *
except Exception as e:
    print '[warning]: experiments in Detector submodule cannot be initialized. error:',
    print e
    pass
