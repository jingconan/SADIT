
import sys
sys.path.append("..")
# from util import *
# from mod_util import *
from mod_util import Attr

class Generator(object):
    pass

import copy
class HarpoonG(Generator):
    """Harpoon Generator, described by
       1. flow_size_mean 2. flow_size_var, 3 flow_arrival_rate
       flow size is normally distributed
       flow arrival is possion distributed
       flow duration is determined by the network condition.
       """
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

    def __getitem__(self, name):
        return self.gen_desc[name]

    def get_new_gen(self, change_para=None):
        new = copy.deepcopy(self)
        if change_para:
            for attr, ratio in change_para.iteritems():
                new.para[attr.lower()] *= ratio
            new.sync()
        return new

class MVGenerator(HarpoonG):
    def sync(self):
        self.para['TYPE'] = 'harpoon'
        self.gen_desc = dict(
                ipsrc = self.para['ipsrc'],
                ipdst = self.para['ipdst'],
                flowsize= 'normal(%f,100)' %(self.para['flow_size']),
                flowstart='exponential(%f)' %(self.para['flow_arrival_rate']),
                sport = 'randomchoice(22,80,443)',
                dport='randomunifint(1025,65535)',
                lossrate='randomchoice(0.001)',
                )

gmap = {'harpoon':HarpoonG,
        'mv':MVGenerator}
def get_generator(gen_desc):
    gen_class = gmap[gen_desc['TYPE']]
    return gen_class(**gen_desc)
