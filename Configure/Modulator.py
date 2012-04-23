import sys
sys.path.append("..")
# from util import *
# from mod_util import *
from mod_util import Attr
class Modulator(object):
    """ * name
        * start
        * profile
        * generator
    """
    def __init__(self, **desc):
        self.desc = desc

    def __getitem__(self, name):
        return self.desc[name]

    def __str__(self):
        return str( Attr(**self.desc) )

    @property
    def profile(self): return self.desc['profile']
    @property
    def start(self): return eval( self.desc['start'] )

from Behaviour import MarkovBehaviour
class MarkovModulator(Modulator, MarkovBehaviour):
    """
        * name
        * start
        * profile
        * generator_states: a list of generator names, representing the states
        * P: transition probability
        * interval: mean of interval time.
    """
    def __init__(self, interval, P, generator_states, **desc):
        Modulator.__init__(self, **desc)
        MarkovBehaviour.__init__(self, interval, P, generator_states)
        self.mod_list = []
        # self.generator_states = generator_states
        # self._gen_modulator_list()
        self.behave_with_profile(self.start, self.profile)


    # def sync(self):
        # self._gen_modulator_list()
        # self.behave_with_profile(self.start, self.profile)

    def __str__(self):
        return ' '.join([str(mod) for mod in self.mod_list])

    def stage(self):
        """for one markov stage"""
        r_start = self.run_para['r_start']
        r_end = self.run_para['r_end']
        mod = Modulator(
                # name=self.desc['name'] + '_' + str(self.mmseq),
                name=self.desc['name'],
                start=r_start,
                profile=( (r_end-r_start,), (1,) ) ,
                generator=self.states[self.cs],
                )
        self.mod_list.append(mod)

from Behaviour import MVBehaviour
class MVModulator(Modulator, MVBehaviour):
    """
    Modulator defines the behaviour of generator within a range of time.
    implement the stage function.
    joint_dist should be numpy array
    """
    def __init__(self, joint_dist, interval, generator_states, **desc):
        Modulator.__init__(self, **desc)
        MVBehaviour.__init__(self, joint_dist, interval, generator_states)
        self.mod_list = []
        self.behave_with_profile(self.start, self.profile)

    def stage(self):
        """for one stage"""
        r_start = self.run_para['r_start']
        r_end = self.run_para['r_end']
        for i in xrange(self.srv_num): # for each destination
            gen = self.states[i][self.cs[i]]
            if not gen:
                continue
            mod = Modulator(
                    name=self.desc['name'],
                    start=r_start,
                    profile=( (r_end-r_start,), (1,) ) ,
                    generator=gen,
                    )
            self.mod_list.append(mod)
