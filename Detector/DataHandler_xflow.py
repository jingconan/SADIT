#!/usr/bin/env python
from DataHandler import PreloadHardDiskFile, HardDiskFileHandler
import re
from time import strptime, mktime
class PreloadHardDiskFile_xflow(PreloadHardDiskFile):
    attr_mapping = { # define the synonym
            'src_ip': 'client_ip',
            'flow_size': 'Cb',
            }

    def _init(self):
        self.fea_vec, self.fea_name = self.parse_xflow(self.f_name)
        self.zip_fea_vec = None
        self.flow_num = len(self.fea_vec)

    def get_fea_slice(self, fea=None, rg=None, rg_type=None, data_order='flow_first'):
        fea = self.attr_mapping.get(fea, fea) # synonym replacement
        PreloadHardDiskFile.__init__(self, fea=None, rg=None, rg_type=None, data_order='flow_first')

    @staticmethod
    def parse_xflow(fileName):
        """
        the input is the filename of the flow file that needs to be parsed.
        the ouput is list of dictionary contains the information for each flow in the data. all these information are strings, users need
        to tranform them by themselves
        """
        flow = []
        # Defines the FORMAT of the data file
        FORMAT = dict()
        FORMAT[11] = dict(
                start_time=0,
                proto=2,
                client_ip=3,
                direction=4,
                server_ip=5,
                Cb=7,
                Cp=8,
                Sb=9,
                Sp=10,
                )
        FORMAT[12] = dict(
                start_time=0,
                proto=3,
                client_ip=4,
                direction=5,
                server_ip=6,
                Cb=8,
                Cp=9,
                Sb=10,
                Sp=11,
                )
        FORMAT[13] = dict(
                start_time=0,
                proto=2,
                client_ip=3,
                # client_port=4,
                direction=5,
                server_ip=6,
                # server_port=7,
                Cb=9,
                Cp=10,
                Sb=11,
                Sp=12,
                )
        FORMAT[14] = dict(
                start_time=0,
                proto=3,
                client_ip=4,
                # client_port=5,
                direction=6,
                server_ip=7,
                # server_port=8,
                Cb=10,
                Cp=11,
                Sb=12,
                Sp=13,
                )
        dotted_to_int = lambda x: [int(val) for val in x.rsplit('.')]
        port_str_to_int = lambda x: int(x[1:])
        attr_convert = lambda x: float( x.rsplit('=')[1].rsplit(',')[0] )
        handler = dict(
                start_time = lambda x: mktime(strptime(x, '%Y%m%d.%H:%M:%S')),
                proto = lambda x: x,
                client_ip = dotted_to_int,
                client_port=port_str_to_int,
                direction=lambda x: x,
                server_ip=dotted_to_int,
                server_port=port_str_to_int,
                Cb= attr_convert,
                Cp= attr_convert,
                Sb= attr_convert,
                Sp= lambda x: float(x.rsplit('=')[1].rsplit('\n')[0]),
                )
        fid = open(fileName, 'r')
        while True:
            line = fid.readline()
            if not line: break
            item = re.split(' ', line)
            # print 'len item', len(item)
            # if len(item) == 12 : print 'item', item
            # print 'item', item
            f = [handler[k](item[v]) for k,v in FORMAT[len(item)].iteritems()]
            flow.append(f)
        fid.close()
        return flow, FORMAT[13].keys()

class HardDiskFileHandler_xflow(HardDiskFileHandler):
    def _init_data(self, f_name):
        self.data = PreloadHardDiskFile_xflow(f_name)

if __name__ == "__main__":
    f = PreloadHardDiskFile_xflow('../../20030902.07.flow.txt')

