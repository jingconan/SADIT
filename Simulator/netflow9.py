#!/usr/bin/python

__author__ = 'jsommers@colgate.edu'

#
# basic netflow9 flow record format
#

import struct
import ipaddr


#
#  template flowset (defines how ip data flowsets are recorded)
#  - flowset id 0 (i16)
#  - length (i16)
#    - template id (i16) (0-255 template/options; >=256 data)
#    - field count (i16)
#    - field type 1 (i16)
#    - field length 1 (i16)
#    - field type 2 (i16)
#    - field length 2 (i16)
#    - field type k (i16)
#    - field length k (i16)
#
#  options template flowset (offers info about the recording process itself, e.g., sampling
#                            rate at an interface)
#  - flowset id 1 (i16)
#  - length (i16)
#  - template id (> 255) (i16)
#  - 
#
#
#  data flowset (an ip data flow, structured according to some template)
#  - flowset id
#  - length
#  - record 1, field value 1
#     - record 1, field value 2
#     - record 1, field value 3
#     - record 1, field value k
#  - record 2, field value 1
#     - record 2, field value 2
#     - record 2, field value 3
#     - record 2, field value k
#  ... padding (each flowset should be 32-bit aligned)
#


class netflow9(object):
    # header
    # version (0x0009) i16
    # messagelen       i16 (number of records)
    # sysuptime        i32 (time in milliseconds since device was booted)
    # unix secs        i32 (standard unix time)
    # seq number       i32 (sequence number of export packets from this device)
    # sourceid         i32 (32 bits that identifies 'exporter observation domain')

    # template
    struct_headertemplate = '!HHIIII'

    struct_rectemplate = '!IIIIHHHHIIIIIBBHHBBBB'

    @classmethod
    def packheader(cls):
        packed = struct.pack(netflow9.struct_headertemplate, 0, 0, 0, 0, 0)
        return packed

    @classmethod
    def packrecord(cls, inputif=0, outputif=0, rtraddr=int(ipaddr.IPAddress('0.0.0.0')), srcaddr=int(ipaddr.IPAddress('0.0.0.0')), dstaddr=int(ipaddr.IPAddress('0.0.0.0')), pkts=0, bytes=0, start=0, end=0, srcport=0, dstport=0, tcpflags=0, ipproto=0, iptos=0, ipnexthop=int(ipaddr.IPAddress('0.0.0.0')), srcas=0, dstas=0, srcmasklen=0, dstmasklen=0, enginetype=0, engineid=0):
        packed = struct.pack(netflow9.struct_rectemplate, rtraddr, srcaddr, dstaddr, inputif, outputif, srcport, dstport, pkts, bytes, ipnexthop, start, end, ipproto, iptos, srcas, dstas, srcmasklen, dstmasklen, tcpflags, enginetype, engineid)
        return packed


def main():
    xbytes = netflow9.packrecord() 
    print 'netflow9 record size:',len(xbytes)

if __name__ == '__main__':
    main()
