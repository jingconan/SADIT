#!/usr/bin/env python

__author__ = 'jsommers@colgate.edu'

from flowlet import *
import struct
import time
import ipaddr
from cflow import cflow


class FlowExporter(object):
    def __init__(self, rname):
        self.routername = rname

    def exportflow(self, ts, flet):
        pass

    def shutdown(self):
        pass


class NullExporter(FlowExporter):
    pass


class TextExporter(FlowExporter):
    def __init__(self, rname):
        FlowExporter.__init__(self, rname)
        outname = self.routername + '_flow.txt'
        self.outfile = open(outname, 'wb')

    def shutdown(self):
        self.outfile.close()

    def exportflow(self, ts, flet):
        print >>self.outfile,'textexport %s %0.06f %s' % (self.routername, ts, str(flet))


class CflowdExporter(FlowExporter):
    def __init__(self, rname):
        FlowExporter.__init__(self, rname)
        outname = self.routername + '.cflowd'
        self.outfile = open(outname, 'wb')

    def shutdown(self):
        self.outfile.close()

    def exportflow(self, ts, flet):
        flowrec = cflow.packrecord(srcaddr=int(ipaddr.IPAddress(flet.srcaddr)), dstaddr=int(ipaddr.IPAddress(flet.dstaddr)), pkts=flet.pkts, bytes=flet.size, start=int(flet.flowstart), end=int(flet.flowend), srcport=flet.srcport, dstport=flet.dstport, tcpflags=flet.tcpflags, ipproto=flet.ipproto, iptos=flet.iptos)
        self.outfile.write(flowrec)


def null_export_factory(rname):
    return NullExporter(rname)

def text_export_factory(rname):
    return TextExporter(rname)

def cflowd_export_factory(rname):
    return CflowdExporter(rname)


def main():
    f1 = Flowlet(ipaddr.IPAddress('10.0.1.1'), ipaddr.IPAddress('192.168.5.2'), 17, 5, 42)
    f1.flowstart = time.time()
    f1.flowend = time.time() + 10
    f1.srcport = 2345
    f1.dstport = 6789

    f2 = copy.copy(f1)
    f2.flowend = time.time() + 20
    f2.ipproto = 6
    f2.tcpflags = 0xff
    f2.srcport = 9999
    f2.dstport = 80
    f2.iptos = 0x08

    textexp = text_export_factory('testrouter')
    textexp.exportflow(time.time(),f1)
    textexp.exportflow(time.time(),f2)
    textexp.shutdown()

if __name__ == '__main__':
    main()
