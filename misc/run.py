#!/usr/bin/env python
import settings

from Configure import gen_anomaly_dot
from Detector import detect

from os import chdir as cd
from os import system as sh
def simulate(total_t, dot_path):
    cd('./Simulator')
    sh( './fs.py %s -t %d' %(dot_path, total_t) )
    cd('..')

def run():
    print 'start configuration'
    gen_anomaly_dot(settings.ANO_LIST,
            settings.NET_DESC,
            settings.NORM_DESC,
            settings.OUTPUT_DOT_FILE)
    print 'start simulation'
    simulate(settings.sim_t,
            settings.OUTPUT_DOT_FILE)
    print 'start detection'
    detector = detect(settings.ROOT + '/Simulator/n0_flow.txt',
            settings.DETECTOR_DESC['win_size'],
            settings.DETECTOR_DESC['fea_option'],
            settings.DETECTOR_DESC['detector_type'],
            )
    detector.plot_entropy()

if __name__ == "__main__":
    run()
