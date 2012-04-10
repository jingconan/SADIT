
import sys
sys.path.append("..")
from util import *

class Generator(object):
    pass

import copy
class HarpoonG(Generator):
    def __init__(self, **para):
        self.para = para
        self.sync()

    def sync(self):
        # import pdb;pdb.set_trace()
        self.gen_desc = dict(
                ipsrc = self.para['ipsrc'],
                ipdst = self.para['ipdst'],
                # flowsize = None,
                flowsize= 'normal(%f,%f)' %(self.para['flow_size_mean'], self.para['flow_size_var']),
                flowstart='exponential(%f)' %(self.para['flow_arrival_rate']),
                sport = 'randomchoice(22,80,443)',
                dport='randomunifint(1025,65535)',
                lossrate='randomchoice(0.001)',
                )

    def __str__(self):
        self.sync()
        return str( Attr(name=self.para['TYPE'], **self.gen_desc) )

    def get_new_gen(self, change_para=None, ratio=None):
        new = copy.deepcopy(self)
        if change_para:
            new.para[change_para.lower()] *= ratio
            new.sync()
        return new

gmap = {'harpoon':HarpoonG}
def get_generator(gen_desc):
    gen_class = gmap[gen_desc['TYPE']]
    return gen_class(**gen_desc)
