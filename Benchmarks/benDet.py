#!/usr/bin/env python
from __future__ import print_function, division
import sys
sys.path.insert(0, "..")
sys.path.insert(0, "../..")
from Detector.Data import MEM_FS


def main():
    for i in xrange(50):
        print('i', i)
        MEM_FS('./n0_flow.txt')
    print('done')
    pass



if __name__ == "__main__":
    main()
