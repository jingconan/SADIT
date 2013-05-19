#!/usr/bin/env python
from __future__ import print_function, division
import sys; sys.path.append('../')
from Detector.Data import HDF_FS
# from pylab import *
import matplotlib.pyplot as plt

class Visualizer(HDF_FS):
    # def __init__(self, f_name):
    #     self.f_name = f_name
    #     data, self.keys = RawParseData(f_name)
    #     self.zip_data = zip(*data)

    # def get(self, name):
    #     idx = self.keys.index(name)
    #     return self.zip_data[idx]

    def vis(self):
        # flow_size = [int(v) for v in self.get('flow_size')]
        # start_time = [float(v) for v in self.get('start_time')]

        flow_size = self.get_rows('flow_size')
        start_time = self.get_rows('start_time')
        min_t = min(start_time)
        start_time = [t-min_t for t in start_time]
        plt.plot(start_time, flow_size)
        plt.xlabel('time')
        plt.ylabel('flow size')
        plt.show()
        pass

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='visualizer of FS data')
    parser.add_argument('file', help='name for the fs data file')
    args, res_args = parser.parse_known_args()
    v = Visualizer(args.file)
    v.vis()
