from __future__ import print_function, division, absolute_import
import unittest
from sadit.Detector.Ident import ComponentFlowStateIdent, ComponentFlowPairIdent
class FlowStateIdentTestCase(unittest.TestCase):
    def setUp(self):
        pass

    def test_get_info_state_by_state(self):
        nu = [0.3, 0.2, 0.1, 0.4]
        nu2 = [0.3, 0.1, 0.1, 0.5]
        nu3 = [0.2, 0.2, 0.1, 0.5]
        mu = [0.25, 0.25, 0.25, 0.25]
        cls = ComponentFlowStateIdent([nu, nu2, nu3,  mu], mu)
        res = cls.get_info_state_by_state(nu, mu)
        cls.set_detect_result([1, 1, 0, 0])
        # print 'self.norm_state_info_mean', cls.norm_state_info_mean
        # self.assertEqual(cls.ano_free_idx, [2, 3])
        res2 = cls.get_state_likelihood([0, 1])

        # print res
        print('res2, ', res2)

class FlowPairTestCase(unittest.TestCase):
    def setUp(self):
        pass

    def test_get_info_state_by_state(self):
        nu = [[0.1, 0.2],
                [0.3, 0.4]]
        mu = [[0.25, 0.25],
                [0.25, 0.25]]
        cls = ComponentFlowPairIdent([nu, mu], mu)
        res = cls.get_info_state_by_state(nu, mu)
        cls.set_detect_result([1, 0])
        res2 = cls.get_state_likelihood([0])


if __name__ == "__main__":
    unittest.main()

