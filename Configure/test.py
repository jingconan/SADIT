#!/usr/bin/env python
########################
### MVBehaviour test ###
########################

from unittest import TestCase, main
from Behaviour import MVBehaviour
import numpy as np

class MultiServer(TestCase):
    def setUp(self):
        joint_dist = np.array([[0.2, 0.1],
                               [0.1, 0.6]])
        self.mv_beh = MVBehaviour(joint_dist, None, 0.1)

    def testBehave(self):
        self.mv_beh.behave(0, 1000)
        self.mv_beh._sample_freq()


if __name__ == "__main__":
    main()


