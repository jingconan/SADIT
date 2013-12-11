#!/usr/bin/env python
"""  convert FS format to (Hierarchical Data Format 5) HDF5 Format
"""
from __future__ import print_function, division
import os
import sys
sys.path.append('../')
sys.path.append('../..')
from Detector import data_map
from sadit.util import tables

def sizeof_fmt(num):
    for x in ['bytes','KB','MB','GB','TB']:
        if num < 1024.0:
            return "%3.1f %s" % (num, x)
        num /= 1024.0

def odf_to_hdf(input_, f_type, out):
    data = data_map[f_type](input_)
    f = tables.open_file(out, 'w')
    g = f.createGroup('/', 'data')
    f.create_table(g, 'table', data.table)
    f.close()
    print('[%s\t%s] successfully stored' % (out,
        sizeof_fmt(os.path.getsize(out))))

# def load_hdf():
#     f = tables.open_file('link1.h5', 'r')
#     import ipdb;ipdb.set_trace()

# fs_to_hdf()
# load_hdf()
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='mem data to hdf')
    parser.add_argument('input', help='path of input data file.')
    parser.add_argument('format', help='The format of input file '
                        'can be [%s]' % ('|'.join(data_map.keys())) )
    parser.add_argument('out', help='path output file (hdf5 format)')
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)
    args = parser.parse_args()
    odf_to_hdf(args.input, args.format, args.out)

