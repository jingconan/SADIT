from __future__ import print_function, division, absolute_import
from .mod_util import Attr

class Generator(object):
    pass

import copy
class HarpoonG(Generator):
    """ Harpoon Generator, described by
           1. flow_size_mean
           2. flow_size_var,
           3 flow_arrival_rate
       `flow size` is normally distributed; `flow arrival` is possion
       distributed; `flow duration` is determined by the network condition.

    Parameters
    ---------------
    ipsrc : str
        source ip address
    ipdst : str
        destination ip address
    flow_size_mean : float
        flow size subjects to normal distribution. It is the mean or the
        normal distribution
    flow_size_var : float
        variance of the flow size distirbution
    flow_arrival_rate : float
        flow arrivals are poission process. It is the rate.
    TYPE : str, 'harpoon' or 'mv'
        type of the modulator

    """

    def __init__(self, **para):
        self.para = para
        self.sync()

    def sync(self):
        """  sync the parameters to self.gen_desc """
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
        """  Generate a new generator accoding to `change_para`

        Parameters
        ---------------
        change_para : dict
            See `Anomaly` for the format of `change_para`

        Returns
        --------------
        new : generator class
            a new generator class

        """
        new = copy.deepcopy(self)
        if change_para is None:
            return new

        # change the parameters
        for attr, ratio in change_para.iteritems():
            if isinstance(ratio, str):
                tp = ratio[0]
                r = float(ratio[1:])
                if tp is '=':
                    new.para[attr.lower()] = r
                elif tp is '+':
                    new.para[attr.lower()] += r
                elif tp is 'x':
                    new.para[attr.lower()] *= r
                else:
                    raise Exception('unknown change parameter')
            # for backward compatibility
            elif isinstance(ratio, float) or isinstance(ratio, int):
                new.para[attr.lower()] *= ratio
        new.sync()
        return new

class MVGenerator(HarpoonG):
    def sync(self):
        """  sync the parameters to self.gen_desc """
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

gmap = {
        'harpoon':HarpoonG,
        'mv':MVGenerator,
        }

def get_generator(gen_desc):
    """  generate generator
    """
    gen_class = gmap[gen_desc['TYPE']]
    return gen_class(**gen_desc)
