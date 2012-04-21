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
        self._gen_modulator_list()

    def sync(self):
        self._gen_modulator_list()

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

    def _gen_modulator_list(self):
        start = eval( self.desc['start'] ) #FIXME
        profile = self.desc['profile']
        for dur, num in zip(*profile):
            end = start + dur
            for i in xrange(num):
                self.behave(start, end)
            start = end

from Behaviour import MVBehaviour
class MVModulator(Modulator, MVBehaviour):
    """implement the stage function. for each stage, add modulator
    using corresponding generator. the profile of modulator is specfied
    as (start_time, duration)"""
    def __init__(self, interval, generator_states, **desc):
        Modulator.__init__(self, **desc)
        MVBehaviour.__init__(self, interval, generator_states)
        self.mod_list = []
        self._gen_modulator_list()

    def stage(self):
        """for one markov stage"""
        r_start = self.run_para['r_start']
        r_end = self.run_para['r_end']
        mod = Modulator(
                name=self.desc['name'],
                start=r_start,
                profile=( (r_end-r_start,), (1,) ) ,
                generator=self.states[self.cs],
                )
        self.mod_list.append(mod)
