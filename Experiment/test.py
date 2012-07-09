#!/usr/bin/env python
from unittest import TestCase, main, skip

from DetectArgSearch import *
class DetectArgSearchUtilTestCase(TestCase):
    def test_get_attr_list(self):
        res = get_attr_list({'good':[1, 2, 3], 'bad':1})
        self.assertEqual(len(res), 1)
        self.assertEqual(res['good'], [1, 2, 3])
        res = get_attr_list({'good':0, 'bad':1})
        self.assertEqual(len(res), 0)
        # test multi level search
        dic = {'good':{'ave':[2]}, 'bad':1}
        res = get_attr_list(dic)
        self.assertEqual(len(res), 1)
        self.assertEqual(res['ave'], [2])
        # test result should be copy of list
        res['ave'][0] = 3
        self.assertEqual(dic['good']['ave'][0], 2)


    def test_change_attr_list(self):
        dic = {'good':[1, 2, 3], 'bad':1}
        res = change_attr_list(dic, 'abc', 123)
        self.assertFalse(res)
        self.assertEqual(dic['good'], [1, 2, 3])
        self.assertEqual(dic['bad'], 1)

        res = change_attr_list(dic, 'good', [2, 3])
        self.assertEqual(dic['good'], [2, 3])
        self.assertTrue(res)

        dic = {1:{2:3}}
        res = change_attr_list(dic, 2, 'c')
        self.assertEqual(dic[1][2], 'c')
        self.assertTrue(res)

        res = change_attr_list(dic, 4, 'c')
        self.assertFalse(res)


class DetectArgSearchTestCase(TestCase):
    def setUp(self):
        pass

    def test_DetectArgSearch(self):
        ANO_ANA_DATA_FILE = './Share/AnoAna.txt'
        self.desc = dict(
            interval=[20, 30],
            win_size=[200, 300],
            win_type='time', # 'time'|'flow'
            fr_win_size=100, # window size for estimation of flow rate
            false_alarm_rate = 0.001,
            unified_nominal_pdf = False, # used in sensitivities analysis
            fea_option = {'dist_to_center':2, 'flow_size':2, 'cluster':2},
            ano_ana_data_file = ANO_ANA_DATA_FILE,
            normal_rg = None,
            detector_type = 'mfmb',
            max_detect_num = 100,
            data_handler = 'fs_deprec',
            flow_file = '../Simulator/n0_flow.txt',
        )
        self.cls = DetectArgSearch(self.desc)
        self.cls.run()


if __name__ == "__main__":
    main()
