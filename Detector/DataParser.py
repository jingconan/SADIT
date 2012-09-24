#!/usr/bin/env python
"""A library of utility function that can parse the data from a specify
type of flow data. If new type of flow format need to be supported, you
can write a new parse function, which is in this file
"""
__author__  = "Jing Conan Wang"
__email__ = "wangjing@bu.edu"

##
# @file DataParser.py
# @brief Parse Flow data
# @author Jing Conan Wang, hbhzwj@gmail.com
# @version 0.0
# @date 2011-10-25


# Format for returned result flow
# flow is a list of dictionary
# dictionary has the following field
# t - Time of the start of the flow
# srcIPStr - the dotted string of src IP address
# srcIP - the long int representation of src IP address
# srcPort - Port number of source
# destIPStr - the dotted string of dest IP address
# destIP - the long int representation of dest IP address
# destPort - port number at the destination


def dottedQuadToNum(ip):
    "convert decimal dotted quad string to long integer"

    hexn = ''.join(["%02X" % long(i) for i in ip.split('.')])
    return long(hexn, 16)

def numToDottedQuad(n):
    "convert long int to dotted quad string"

    d = 256 * 256 * 256
    q = []
    while d > 0:
        m,n = divmod(n,d)
        q.append(str(m))
        d = d/256

    return '.'.join(q)

def ParseData(fileName):
    """
    the input is the filename of the flow file that needs to be parsed.
    the ouput is list of dictionary contains the information for each flow in the data.
    """
    flow = []
    FORMAT = dict(t=3, IP_Port=5, protocol=6, flowSize=10, endT=4) # Defines the FORMAT of the data file
    fid = open(fileName, 'r')
    while True:
        line = fid.readline()
        if not line or line[0:10] != 'textexport':
            break
        if line == '\n': # Ignore Blank Line
            continue
        item = line.rsplit(' ')
        # print 'item Length: ' + str(len(item))
        f = dict()
        # print FORMAT
        for k, v in FORMAT.iteritems():
            if k == 'flowSize' or k == 't' or k == 'endT':
                f[k] = float(item[v])
            elif k == 'IP_Port':
                sd = item[v].rsplit('->')
                if len(sd) != 2:
                    raise ValueError('Format Incorrect')
                [srcIPStr, srcPortStr] = sd[0].rsplit(':')
                f['srcIPStr'] = srcIPStr
                f['srcIP'] = dottedQuadToNum(srcIPStr)
                f['srcPort'] = int(srcPortStr)
                IPDigit = srcIPStr.rsplit('.')
                f['srcIPVec'] = (int(IPDigit[0]), int(IPDigit[1]), int(IPDigit[2]), int(IPDigit[3]) )

                [destIPStr, destPortStr] = sd[1].rsplit(':')
                f['destIPStr'] = destIPStr
                f['destIP'] = dottedQuadToNum(destIPStr)
                f['destPort'] = int(destPortStr)
                IPDigit = destIPStr.rsplit('.')
                f['destIPVec'] = (int(IPDigit[0]), int(IPDigit[1]), int(IPDigit[2]), int(IPDigit[3]) )
            else:
                f[k] = item[v]

        # print f
        flow.append(f)

    fid.close()

    return flow

import re
from util import argsort
def RawParseData(fileName):
    """
    the input is the filename of the flow file that needs to be parsed.
    the ouput is list of dictionary contains the information for each flow in the data. all these information are strings, users need
    to tranform them by themselves
    """
    flow = []
    # FORMAT = dict(start_time=3, end_time=4, src_ip=5, sc_port=6, octets=13, ) # Defines the FORMAT of the data file
    FORMAT = dict(start_time=3, end_time=4, src_ip=5, sc_port=6, flow_size=13, ) # Defines the FORMAT of the data file
    fid = open(fileName, 'r')
    t = []
    while True:
        line = fid.readline()
        if not line or line[0:10] != 'textexport':
            break
        if line == '\n': # Ignore Blank Line
            continue
        item = re.split('[ :>]', line) #FIXME need to be changed if want to use port information
        f = [item[v] for k,v in FORMAT.iteritems()]
        flow.append(f)
        t.append(item[FORMAT['start_time']])

    fid.close()

    arg_t = argsort(t)
    sort_flow = [flow[i] for i in arg_t ]
    return sort_flow, FORMAT.keys()


if __name__ == "__main__":
    ParseData('./data/data3a.txt')



