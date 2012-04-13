import sys
sys.path.append("..")
from util import *
from mod_util import *
class Modulator(object):
    def __init__(self, **desc):
        self.desc = desc

    def __getitem__(self, name):
        return self.desc[name]

    def __str__(self):
        # print 'self.desc, ', self.desc
        return str( Attr(**self.desc) )


