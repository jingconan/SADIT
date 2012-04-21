#!/usr/bin/env python
"""This file defines the behaviour of """
import sys
sys.path.append("..")
from util import TO_CLS, abstract_method
from random import randint
from mod_util import RandDist

class Behaviour(object):
    def stage(): abstract_method()
    def behave(): abstract_method()

from random import expovariate as exponential
class MarkovBehaviour(Behaviour):
    """Markov behaviour is a kinf of behaviour that can """
    def __init__(self, interval, P, states):
        Behaviour.__init__(self)
        exec TO_CLS('interval', 'P', 'states')
        sn = len(states)
        self.cs = randint(0, sn-1) # cs: current state
        self.run_para = None

    def stage(self):
        abstract_method()

    def behave(self, start, end):
        t = start
        while t <= end:
            self.cs = self.get_new_state()
            inter = self.get_interval()
            self.run_para = dict(r_start=t, r_end=t+inter)
            self.stage()
            t += inter

    def get_new_state(self):
        return RandDist(self.P[self.cs])

    def get_interval(self):
        return exponential(1.0 / self.interval)

import numpy as np
class MVBehaviour(MarkovBehaviour):
    """The traffic is generated according to multi-variable distribution
    if there are m servers, then the joint distribution will be m dimension
    matrix. For each component, there are n possible values. So we need m*n
    possible generators
    """
    def __init__(self, joint_dist, generator_states, interval):
        self.joint_dist = joint_dist
        self.generator_states = generator_states
        self.interval = interval
        self.record = []

    @property
    def dim(self): return self.joint_dist.shape

    def get_sample(self):
        assert(np.sum(self.joint_dist) == 1 )
        x = RandDist( self.joint_dist.ravel() )
        idx = np.unravel_index(x, self.dim)
        return idx

    def get_new_state(self):
        ns = self.get_sample()
        self.record.append(ns)
        return ns

    def get_interval(self):
        return self.interval

    def _sample_freq(self):
        freq = np.zeros(self.dim)
        for r in self.record:
            freq[r] += 1
        freq /= np.sum(freq)
        print 'freq, ', freq
