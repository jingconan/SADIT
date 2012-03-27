#!/usr/bin/env python

__author__ = 'jsommers@colgate.edu'

#
# header definitions copied from dave plonka's
# cflowd perl module
#

import struct
import ipaddr

class cflow(object):
    k_routerMask        = 0x00000001 
    k_srcIpAddrMask     = 0x00000002 
    k_dstIpAddrMask     = 0x00000004 
    k_inputIfIndexMask  = 0x00000008 
    k_outputIfIndexMask = 0x00000010 
    k_srcPortMask       = 0x00000020 
    k_dstPortMask       = 0x00000040 
    k_pktsMask          = 0x00000080 
    k_bytesMask         = 0x00000100 
    k_ipNextHopMask     = 0x00000200 
    k_startTimeMask     = 0x00000400 
    k_endTimeMask       = 0x00000800 
    k_protocolMask      = 0x00001000 
    k_tosMask           = 0x00002000 
    k_srcAsMask         = 0x00004000 
    k_dstAsMask         = 0x00008000 
    k_srcMaskLenMask    = 0x00010000 
    k_dstMaskLenMask    = 0x00020000 
    k_tcpFlagsMask      = 0x00040000 
    k_engineTypeMask    = 0x00400000 
    k_engineIdMask      = 0x00800000 

    k_fullmask = 0x00c7ffff

    struct_template = '!IIIIHHHHIIIIIBBHHBBBBB'

    @classmethod
    def packrecord(cls, inputif=0, outputif=0, rtraddr=int(ipaddr.IPAddress('0.0.0.0')), srcaddr=int(ipaddr.IPAddress('0.0.0.0')), dstaddr=int(ipaddr.IPAddress('0.0.0.0')), pkts=0, bytes=0, start=0, end=0, srcport=0, dstport=0, tcpflags=0, ipproto=0, iptos=0, ipnexthop=int(ipaddr.IPAddress('0.0.0.0')), srcas=0, dstas=0, srcmasklen=0, dstmasklen=0, enginetype=0, engineid=0):
        packed = struct.pack(cflow.struct_template, cflow.k_fullmask, rtraddr, srcaddr, dstaddr, inputif, outputif, srcport, dstport, pkts, bytes, ipnexthop, start, end, ipproto, iptos, srcas, dstas, srcmasklen, dstmasklen, tcpflags, enginetype, engineid)
        return packed


def main():
    xbytes = cflow.packrecord() 
    print 'cflow record size:',len(xbytes)

if __name__ == '__main__':
    main()
