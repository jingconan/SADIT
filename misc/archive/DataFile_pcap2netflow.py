#!/usr/bin/env python
import re

def get_ip_port(val):
    ip_tmp, port = val.rsplit(':')
    ip = ip_tmp[1:-1]
    return ip, port

def ParseData_pcap2netflow(fileName):
    """
    the input is the filename of the flow file that needs to be parsed.
    the ouput is list of dictionary contains the information for each flow in the data. all these information are strings, users need
    to tranform them by themselves
    """
    flow = []
    # FORMAT = dict(start_time=3, end_time=4, src_ip=5, sc_port=6, octets=13, ) # Defines the FORMAT of the data file
    fid = open(fileName, 'r')
    while True:
        line = fid.readline()
        if not line or not line.startswith('FLOW'):
            break
        if line == '\n': # Ignore Blank Line
            continue
        item = re.split('[ ]', line) #FIXME need to be changed if want to use port information
        f = dict()
        for i in xrange(1, len(item)-1, 2):
            f[item[i]] = item[i+1]
        src_ip, src_port = get_ip_port(f['src'])
        dst_ip, dst_port = get_ip_port(f['dst'])
        f['src_ip'] = src_ip
        f['src_port'] = src_port
        f['dst_ip'] = dst_ip
        f['dst_port'] = dst_port
        f['flow_size'] = f['octets']

        flow.append(f.values())
    fid.close()

    if not flow: raise Exception('Not even a flow is found. Are you specifying the right filename?')

    return flow, f.keys()

from DataFile import PreloadHardDiskFile

class PreloadHardDiskFile_pcap2netflow(PreloadHardDiskFile):
    def _init(self):
        self.fea_vec, self.fea_name = ParseData_pcap2netflow(self.f_name)
        self.zip_fea_vec = None
        self.flow_num = len(self.fea_vec)

from DataFile import HardDiskFileHandler
class HardDiskFileHandler_pcap2netflow(HardDiskFileHandler):
    def _init_data(self, f_name):
        self.data = PreloadHardDiskFile_pcap2netflow(f_name)

# from Detector_basic import ModelFreeAnoDetector, ModelBaseAnoDetector, FBAnoDetector
# def detect_pcap2netflow(f_name, win_size, fea_option, detector_type, detector_desc):
#     """An function for convenience
#     - *f_name* the name or a list of name for the flow file.
#     - *win_size* the window size
#     - *fea_option*

#     """
#     detector_map = {
#             'mf':ModelFreeAnoDetector,
#             'mb':ModelBaseAnoDetector,
#             'mfmb':FBAnoDetector,
#             }
#     data_file = HardDiskFileHandler_pcap2netflow(f_name, win_size, fea_option)
#     detector = detector_map[detector_type](detector_desc)
#     detector(data_file)
#     return detector
