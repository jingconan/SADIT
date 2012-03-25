#!/usr/bin/env python

__author__ = 'jsommers@colgate.edu'

#
# basic ipfix flow record format
#

import struct
import ipaddr

class ipfix(object):
    # header
    # version (0x000a) i16
    # messagelen       i16
    # export timestamp i32
    # seq number       i32
    # sourceid         i32

    # template
    struct_headertemplate = '!HHIII'

    struct_rectemplate = '!IIIIHHHHIIIIIBBHHBBBB'

    @classmethod
    def packheader(cls):
        packed = struct.pack(ipfix.struct_headertemplate, 0, 0, 0, 0, 0)
        return packed

    @classmethod
    def packrecord(cls, inputif=0, outputif=0, rtraddr=int(ipaddr.IPAddress('0.0.0.0')), srcaddr=int(ipaddr.IPAddress('0.0.0.0')), dstaddr=int(ipaddr.IPAddress('0.0.0.0')), pkts=0, bytes=0, start=0, end=0, srcport=0, dstport=0, tcpflags=0, ipproto=0, iptos=0, ipnexthop=int(ipaddr.IPAddress('0.0.0.0')), srcas=0, dstas=0, srcmasklen=0, dstmasklen=0, enginetype=0, engineid=0):
        packed = struct.pack(ipfix.struct_rectemplate, rtraddr, srcaddr, dstaddr, inputif, outputif, srcport, dstport, pkts, bytes, ipnexthop, start, end, ipproto, iptos, srcas, dstas, srcmasklen, dstmasklen, tcpflags, enginetype, engineid)
        return packed


def main():
    xbytes = ipfix.packrecord() 
    print 'ipfix record size:',len(xbytes)

if __name__ == '__main__':
    main()
