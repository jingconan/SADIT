#!/usr/bin/env python

__author__ = 'jsommers@colgate.edu'

import random
import copy
import ipaddr
import socket
import time


class IncompatibleFlowlets(Exception):
    pass


class FiveTuple(object):
    __slots__ = ['key']
    def __init__(self, saddr, daddr, ipproto, sport=0, dport=0):
        # truly store the five-tuple as a py tuple for efficiency
        self.key = (saddr, daddr, ipproto, sport, dport)

    def mkreverse(self):
        rv = FiveTuple(self.key[1], self.key[0], self.key[2], self.key[4], self.key[3])
        return rv


class Flowlet(object):
    __slots__ = ['__mss','__iptos','__pkts','__bytes','fivetuple','xtype','xdata','__tcpflags','__ackflow','__flowstart','__flowend','ingress_intf', 'anoFlag']
    def __init__(self, ft=None, pkts=0, bytes=0, tcpflags=0, xtype='flowlet', xdata=None):
        self.xtype = xtype
        self.xdata = xdata
        self.fivetuple = ft
        self.pkts = pkts
        # print 'bytes ', bytes
        self.bytes = bytes
        self.ingress_intf = None
        self.iptos = 0x0
        self.mss = 1500
        self.tcpflags = 0x0
        self.__flowstart = -1.0
        self.__flowend = -1.0
        self.ackflow = False

# Add By Jing Wang
        self.anoFlag = False
# End Add By Jing Wang

    @property
    def iptos(self):
        return self.__iptos

    @iptos.setter
    def iptos(self, iptos):
        self.__iptos = iptos

    @property
    def mss(self):
        return self.__mss

    @mss.setter
    def mss(self, m):
        assert(100 <= m <= 1500)
        self.__mss = m

    @property
    def endofflow(self):
        # check if tcp and FIN or RST
        return self.ipproto == socket.IPPROTO_TCP and (self.tcpflags & 0x01 or self.tcpflags & 0x04)

    @property
    def key(self):
        return self.fivetuple.key

    @property
    def size(self):
        return self.bytes

    @property
    def srcaddr(self):
        return self.fivetuple.key[0]

    @property
    def dstaddr(self):
        return self.fivetuple.key[1]

    @property
    def ipproto(self):
        return self.fivetuple.key[2]

    @property
    def ipprotoname(self):
        if self.ipproto == socket.IPPROTO_TCP:
            return 'tcp'
        elif self.ipproto == socket.IPPROTO_UDP:
            return 'udp'
        elif self.ipproto == socket.IPPROTO_ICMP:
            return 'icmp'
        else:
            return 'ip'

    @property
    def srcport(self):
        return self.fivetuple.key[3]

    @property
    def dstport(self):
        return self.fivetuple.key[4]

    @property
    def pkts(self):
        return self.__pkts

    @pkts.setter
    def pkts(self, p):
        assert(p >= 0)
        self.__pkts = p

    @property
    def bytes(self):
        return self.__bytes

    @bytes.setter
    def bytes(self, b):
        assert(b >= 0)
        self.__bytes = b

    @property
    def ackflow(self):
        return self.__ackflow

    @ackflow.setter
    def ackflow(self, a):
        self.__ackflow = a;

    def clear_tcp_flags(self):
        self.__tcpflags = 0x0

    def add_tcp_flag(self, flag):
        self.__tcpflags |= flag

    @property
    def tcpflags(self):
        return self.__tcpflags

    @tcpflags.setter
    def tcpflags(self, flags):
        self.__tcpflags = flags

    @property
    def tcpflagsstr(self):
        rv = []
        if self.tcpflags & 0x01: #fin
            rv.append('F')
        if self.tcpflags & 0x02: #syn
            rv.append('S')
        if self.tcpflags & 0x04: #rst
            rv.append('R')
        if self.tcpflags & 0x08: #push
            rv.append('P')
        if self.tcpflags & 0x10: #ack
            rv.append('A')
        if self.tcpflags & 0x20: #urg
            rv.append('U')
        if self.tcpflags & 0x40: #ece
            rv.append('E')
        if self.tcpflags & 0x80: #cwr
            rv.append('C')
        return ''.join(rv)

    @property
    def flowstart(self):
        return self.__flowstart

    @flowstart.setter
    def flowstart(self, fstart):
        assert (fstart >= 0)
        self.__flowstart = fstart

    @property
    def flowend(self):
        return self.__flowend

    @flowend.setter
    def flowend(self, fend):
        assert (fend >= 0)
        assert (fend >= self.flowstart)
        self.__flowend = fend

    def __cmp__(self, other):
        return cmp(self.key, other.key)

    def __iadd__(self, other):
        assert(self.key == other.key)
        self.pkts += other.pkts
        self.bytes += other.bytes
        self.tcpflags |= other.tcpflags
        return self

    def __add__(self, other):
        assert(self.key == other.key)
        rv = copy.copy(self)
        rv.pkts += other.pkts
        rv.bytes += other.bytes
        rv.tcpflags |= other.tcpflags
        return rv

    def __str__(self):
        return "%0.06f %0.06f %s:%d->%s:%d %s 0x%0x %s %d %d %s" % (self.flowstart, self.flowend, self.srcaddr, self.srcport, self.dstaddr, self.dstport, self.ipprotoname, self.iptos, self.ingress_intf, self.pkts, self.bytes, self.tcpflagsstr)


if __name__ == '__main__':
    ft = FiveTuple(str(ipaddr.IPAddress('10.0.1.1')), str(ipaddr.IPAddress('192.168.5.2')), 17, 5, 42)
    f1 = Flowlet(ft)
    f1.flowstart = time.time()
    f1.flowend = time.time() + 10
    print f1.key
    print str(f1)

    # NB: shallow copy of f1; flow key will be identical
    f2 = copy.copy(f1)
    f2.flowend = time.time() + 20
    f2.tcpflags = 0xff
    f2.iptos = 0x08

    # test whether fivetuple keys referred to by each flowlet
    # are the same object
    print 'flowkey objects are the same:',f2.key is f1.key

    print f2.key
    print str(f2)
