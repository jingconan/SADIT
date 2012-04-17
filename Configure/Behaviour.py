#!/usr/bin/env python
"""This file defines the behaviour of """
from mod_util import *
from util import *
class Behaviour(object):
    def run(): abstract_method()
    def behave(): abstract_method()

from random import expovariate as exponential
class MarkovBehaviour(object):
    """Markov behaviour is a kinf of behaviour that can """
    def __init__(self, interval, P, states):
        exec TO_CLS('interval', 'P', 'states')
        sn = len(states)
        self.cs = random.randint(0, sn-1) # cs: current state
        self.run_para = None

    def stage(self):
        abstract_method()

    def behave(self, start, end):
        t = start
        while t <= end:
            self.cs = RandDist(self.P[self.cs])
            inter = exponential(1.0 / self.interval)
            self.run_para = dict(r_start=t, r_end=t+inter)
            self.stage()
            t += inter


