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

    def get_new_state(self):
        # return RandDist(self.P[self.cs])
        return RandDist(self.P) # FIXME use stationary prob

    def get_interval(self):
        # return exponential(1.0 / self.interval)
        return self.interval

    def behave_with_profile(self, start, profile):
        for dur, num in zip(*profile):
            end = start + dur
            for i in xrange(num):
                self.behave(start, end)
            start = end

    def behave(self, start, end):
        t = start
        while t <= end:
            self.cs = self.get_new_state()
            inter = self.get_interval()
            self.run_para = dict(r_start=t, r_end=t+inter)
            self.stage()
            t += inter

try:
    import numpy as np
except:
    print '[Warning] MultiServer Detector requires numpy'

class MVBehaviour(MarkovBehaviour):
    """
    Description:
        - will make choice every other t time.
        - the generators is selected according to multi-variate distribution

    Required Variables:
        - states: states for all possible value. it is a list of list,
            the first dimension is the id of servers, the second dimension is the possible
            for type of generator for a specific server.
        - joint_dist: the joint distribution for indicator variable to each server.

    The traffic is generated according to multi-variable distribution
    if there are m servers, then the joint distribution will be m dimension
    matrix. For each component, there are n possible values. So we need m*n
    possible generators
    """
    def __init__(self, joint_dist, interval, generator_states):
        self.joint_dist = joint_dist
        self.states = generator_states
        self.interval = interval
        self.record = []

    @property
    def dim(self): return self.joint_dist.shape

    @property
    def srv_num(self): return len(self.dim)

    def get_sample(self):
        """generate a sample according to joint distribution"""
        # assert(np.sum(self.joint_dist) == 1 )
        assert( abs( np.sum(self.joint_dist) - 1) < 1e-3)
        x = RandDist( self.joint_dist.ravel() )
        idx = np.unravel_index(x, self.dim)
        return idx

    def get_new_state(self):
        ns = self.get_sample()
        self.record.append(ns)
        return ns

    def get_interval(self):
        return self.interval
        # return exponential(1.0 / self.interval)

    def _sample_freq(self):
        freq = np.zeros(self.dim)
        for r in self.record:
            freq[r] += 1
        freq /= np.sum(freq)
        print 'freq, ', freq

