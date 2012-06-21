#!/usr/bin/env python
import sys
sys.path.append("..")
sys.path.append("../..")
from Detector import *
def test_pcap2netflow():
    ANO_ANA_DATA_FILE = './test_AnoAna.txt'
    DETECTOR_DESC = dict(
            # interval=30,
            # interval=500,
            # win_size = 50,
            interval=4,
            win_size = 10,
            # win_size=4000,
            win_type='flow', # 'time'|'flow'
            fr_win_size=100, # window size for estimation of flow rate
            false_alarm_rate = 0.001,
            unified_nominal_pdf = False, # used in sensitivities analysis
            # discrete_level = DISCRETE_LEVEL,
            # cluster_number = CLUSTER_NUMBER,
            fea_option = {'dist_to_center':2, 'flow_size':2, 'cluster':2},
            # fea_option = {'dist_to_center':2, 'octets':2, 'cluster':2},
            # fea_option = {'dist_to_center':2, 'flow_size':2, 'cluster':1},
            ano_ana_data_file = ANO_ANA_DATA_FILE,
            detector_type = 'mfmb',
            normal_rg = None,
            max_detect_num = None,
            )
    desc = DETECTOR_DESC
    # detector = detect_pcap2netflow('../../CyberData/simple_pkt/loc1-20020523-1835.flow', desc['win_size'],
            # desc['fea_option'], 'mfmb', desc)

    # detector = detect_pcap2netflow('../../CyberData/simple_pkt/l06t01.flow', desc['win_size'],
            # desc['fea_option'], 'mfmb', desc)


    f_name = './toolsmith.flow'
    # f_name ='/home/wangjing/LocalResearch/CyberData/simple_pkt/loc3-20030902-0930.flow'
    detector = detect_pcap2netflow(f_name, desc['win_size'],
            desc['fea_option'], 'mfmb', desc)
    # detector.plot_entropy(pic_show=False, pic_name="./test_pcap2netflow.eps")
    detector.plot_entropy(pic_show=False, pic_name="./test_pcap2netflow.png")

def test_pcap2netflow_loc1():
    ANO_ANA_DATA_FILE = './test_AnoAna.txt'
    DETECTOR_DESC = dict(
            interval=500,
            win_size = 500,
            win_type='flow', # 'time'|'flow'
            fr_win_size=100, # window size for estimation of flow rate
            false_alarm_rate = 0.001,
            unified_nominal_pdf = False, # used in sensitivities analysis
            fea_option = {'dist_to_center':2, 'flow_size':2, 'cluster':2},
            ano_ana_data_file = ANO_ANA_DATA_FILE,
            detector_type = 'mfmb',
            normal_rg = None,
            max_detect_num = None,
            )
    desc = DETECTOR_DESC

    f_name ='/home/wangjing/LocalResearch/CyberData/simple_pkt/loc1-20020523-1835.flow'
    detector = detect_pcap2netflow(f_name, desc['win_size'],
            desc['fea_option'], 'mfmb', desc)
    # detector.plot_entropy(pic_show=False, pic_name="./test_pcap2netflow_loc2.eps")
    detector.plot_entropy(pic_show=False, pic_name="./test_pcap2netflow_loc1.png")



def test_pcap2netflow_loc2():
    ANO_ANA_DATA_FILE = './test_AnoAna.txt'
    DETECTOR_DESC = dict(
            interval=50,
            win_size = 100,
            win_type='flow', # 'time'|'flow'
            fr_win_size=100, # window size for estimation of flow rate
            false_alarm_rate = 0.001,
            unified_nominal_pdf = False, # used in sensitivities analysis
            fea_option = {'dist_to_center':2, 'flow_size':2, 'cluster':2},
            ano_ana_data_file = ANO_ANA_DATA_FILE,
            detector_type = 'mfmb',
            normal_rg = None,
            max_detect_num = None,
            )
    desc = DETECTOR_DESC

    f_name ='/home/wangjing/LocalResearch/CyberData/simple_pkt/loc2-20030513-1005.flow'
    detector = detect_pcap2netflow(f_name, desc['win_size'],
            desc['fea_option'], 'mfmb', desc)
    # detector.plot_entropy(pic_show=False, pic_name="./test_pcap2netflow_loc2.eps")
    detector.plot_entropy(pic_show=False, pic_name="./test_pcap2netflow_loc2.png")


def test_pcap2netflow_loc3():
    ANO_ANA_DATA_FILE = './test_AnoAna.txt'
    DETECTOR_DESC = dict(
            interval=5000,
            win_size = 4000,
            win_type='flow', # 'time'|'flow'
            fr_win_size=100, # window size for estimation of flow rate
            false_alarm_rate = 0.001,
            unified_nominal_pdf = False, # used in sensitivities analysis
            fea_option = {'dist_to_center':2, 'flow_size':2, 'cluster':2},
            ano_ana_data_file = ANO_ANA_DATA_FILE,
            detector_type = 'mfmb',
            normal_rg = None,
            max_detect_num = None,
            )
    desc = DETECTOR_DESC

    f_name ='/home/wangjing/LocalResearch/CyberData/simple_pkt/loc3-20030902-0930.flow'
    detector = detect_pcap2netflow(f_name, desc['win_size'],
            desc['fea_option'], 'mfmb', desc)
    detector.plot_entropy(pic_show=False, pic_name="./test_pcap2netflow_loc3.eps")

def test_pcap2netflow_loc4():
    ANO_ANA_DATA_FILE = './test_AnoAna.txt'
    DETECTOR_DESC = dict(
            interval=500,
            win_size = 500,
            win_type='flow', # 'time'|'flow'
            fr_win_size=100, # window size for estimation of flow rate
            false_alarm_rate = 0.001,
            unified_nominal_pdf = False, # used in sensitivities analysis
            fea_option = {'dist_to_center':2, 'flow_size':2, 'cluster':2},
            ano_ana_data_file = ANO_ANA_DATA_FILE,
            detector_type = 'mfmb',
            normal_rg = None,
            max_detect_num = None,
            )
    desc = DETECTOR_DESC

    f_name ='/home/wangjing/LocalResearch/CyberData/simple_pkt/loc4-20040206-0410.flow'
    detector = detect_pcap2netflow(f_name, desc['win_size'],
            desc['fea_option'], 'mfmb', desc)
    detector.plot_entropy(pic_show=False, pic_name="./test_pcap2netflow_loc4.png")

def test_pcap2netflow_loc5():
    ANO_ANA_DATA_FILE = './test_AnoAna.txt'
    DETECTOR_DESC = dict(
            interval=500,
            win_size = 500,
            win_type='flow', # 'time'|'flow'
            fr_win_size=100, # window size for estimation of flow rate
            false_alarm_rate = 0.001,
            unified_nominal_pdf = False, # used in sensitivities analysis
            fea_option = {'dist_to_center':2, 'flow_size':2, 'cluster':2},
            ano_ana_data_file = ANO_ANA_DATA_FILE,
            detector_type = 'mfmb',
            normal_rg = None,
            max_detect_num = None,
            )
    desc = DETECTOR_DESC

    f_name ='/home/wangjing/LocalResearch/CyberData/simple_pkt/loc5-20031205-1431.flow'
    detector = detect_pcap2netflow(f_name, desc['win_size'],
            desc['fea_option'], 'mfmb', desc)
    detector.plot_entropy(pic_show=False, pic_name="./test_pcap2netflow_loc5.png")





if __name__ == "__main__":
    # test_pcap2netflow()
    import time
    start_t = time.clock()
    # test_pcap2netflow_loc1()
    # test_pcap2netflow_loc2()
    # test_pcap2netflow_loc3()
    # test_pcap2netflow_loc4()
    test_pcap2netflow_loc5()
    end_t = time.clock()
    print 'total running time is: %f'%(end_t - start_t)



