#!/usr/bin/env python

__author__ = 'jsommers@colgate.edu'

# import cProfile as profile
import heapq
import sys
import ipaddr
import networkx
from networkx.algorithms.traversal.path import single_source_dijkstra_path, dijkstra_path_length
import pydot
import random
import signal
import socket
import radix
import logging
from optparse import OptionParser
# import gc

from flowlet import *
from traffic import *
from flowexport import *

# Add By Jing Wang
def argsort(seq):
    # http://stackoverflow.com/questions/3071415/efficient-method-to-calculate-the-rank-vector-of-a-list-in-python
    return sorted(range(len(seq)), key=seq.__getitem__)


class InvalidRoutingConfiguration(Exception):
    pass


class Simulator(object):
    def __init__(self, interval, config, exportfn, endtime=1.0, debug=False, progtick=0.05, snmpexportinterval=0, snmpexportfile=None):
        self.debug = debug
        self.__interval = interval
        self.__now = time.time()
        self.heap = []
        self.graph = None
        self.routing = None
        self.__exportfn = exportfn
        self.endtime = endtime
        self.starttime = self.__now
        self.intr = False
        self.progtick = progtick
        self.snmpexportinterval = snmpexportinterval
        self.snmpexportfile = snmpexportfile
        self.logger = logging.getLogger('flowmax')
        if self.debug:
            logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
        else:
            logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
        self.__loadconfig(config)
        self.after(0.0, 'progress indicator', self.progress)

    def progress(self):
        complete = (self.now - self.starttime) / float(self.endtime)
        self.logger.info('simulation completion: %2.2f' % (complete))
        self.after(self.endtime*self.progtick, 'progress indicator', self.progress)

    def sighandler(self, signum, stackframe):
        self.intr = True

    @property
    def now(self):
        return self.__now

    def after(self, delay, evid, fn, *fnargs):
        expire_time = self.now + delay
        heapq.heappush(self.heap, (expire_time, evid, fn, fnargs))


    @property
    def interval(self):
        return self.__interval


    def __configure_edge_reliability(self, a, b, relistr, edict):
        # 'reliability': '"failureat=10 downfor=5"'
        # 'reliability': '"mttf=exponential(0.1) mttr=exponential(0.001)"'

        relidict = mkdict(relistr.replace('"', '').strip())
        # print relidict

        ttf = ttr = None
        for k,v in relidict.iteritems():
            if k == 'failureafter':
                ttf = eval(v)
                # print 'fat',ttf
                if isinstance(ttf, (int, float)):
                    ttf = modulation_generator([ttf])

            elif k == 'downfor':
                ttr = eval(v)
                # print 'downf',ttr
                if isinstance(ttr, (int, float)):
                    ttr = modulation_generator([ttr])

            elif k == 'mttf':
                ttf = eval(v)

            elif k == 'mttr':
                ttr = eval(v)

        # print 'ttf',ttf
        # print 'ttr',ttr

        if ttf or ttr:
            assert(ttf and ttr)
            xttf = next(ttf)
            # print 'failing link after %f seconds' % (xttf)
            self.after(xttf, 'link-failure-'+a+'-'+b, self.__linkdown, a, b, edict, ttf, ttr)



    def __loadconfig(self, config):
        self.graph = networkx.nx_pydot.read_dot(config)
        for a,b,d in self.graph.edges(data=True):
            w = 1
            if 'weight' in d:
                w = d['weight']
            d['weight'] = int(w)

            if 'reliability' in d:
                self.__configure_edge_reliability(a,b,d['reliability'],d)

        if self.debug:
            for a,b,d in self.graph.edges_iter(data=True):
                print a,b,d

        self.__configure_routing()
        self.__configure_parallel_universe()
        self.__configure_traffic()


    def __configure_routing(self):
        self.routing = {}
        for n in self.graph:
            self.routing[n]=single_source_dijkstra_path(self.graph,n)
        # self.routing = all_pairs_shortest_path(self.graph)
        # print self.routing
        if self.debug:
            for n,d in self.graph.nodes_iter(data=True):
                print n,d

        self.ipdestlpm = radix.Radix()
        # self.ipdestlist = []
        for n,d in self.graph.nodes_iter(data=True):
            dlist = d['ipdests'].split(' ')
            if self.debug:
                print dlist,n
            for destipstr in dlist:
                destipstr = destipstr.replace('"','')
                ipnet = ipaddr.IPNetwork(destipstr)
                # self.ipdestlist.append( (ipnet, n) )
                xnode = self.ipdestlpm.add(str(ipnet))
                if 'dests' in xnode.data:
                    xnode.data['dests'].append(n)
                else:
                    xnode.data['net'] = ipnet
                    xnode.data['dests'] = [ n ]

        self.owdhash = {}
        for a in self.graph:
            for b in self.graph:
                key = a + ':' + b

                rlist = [ a ]
                while rlist[-1] != b:
                    nh = self.nexthop(rlist[-1], b)
                    if not nh:
                        self.logger.debug('No route from %s to %s (in owd; ignoring)' % (a,b))
                        return None
                    rlist.append(nh)

                owd = 0.0
                for i in xrange(len(rlist)-1):
                    owd += self.delay(rlist[i],rlist[i+1])
                self.owdhash[key] = owd


    def __addupd_router(self, rname, rdict):
        robj = None
        if rname not in self.routers:
            aa = 'False'
            if 'autoack' in rdict:
                aa = rdict['autoack']
            aa = eval(aa.replace('"', ''))
            if self.debug:
                print 'adding router',rname,rdict,'autoack',aa
            robj = Router(rname, self, self.__exportfn, snmpexportinterval=self.snmpexportinterval, snmpexportfile=self.snmpexportfile, autoack=aa, debug=self.debug)
            self.routers[rname] = robj
        else:
            robj = self.routers[rname]
        return robj


    def __configure_parallel_universe(self):
        '''
        using the the networkx graph stored in the simulator,
        build corresponding Routers and Links in the sim world.
        '''
        self.routers = {}

        for rname,rdict in self.graph.nodes_iter(data=True):
            self.__addupd_router(rname, rdict)

        for a,b,d in self.graph.edges_iter(data=True):
            if self.debug:
                print a,b,d

            ra = self.__addupd_router(a, d)
            rb = self.__addupd_router(b, d)

            cap = self.capacity(a,b)
            delay = self.delay(a,b)
            ra.add_link(Link(self, cap/8, delay, ra, rb), b)
            rb.add_link(Link(self, cap/8, delay, rb, ra), a)


    def __configure_traffic(self):
        self.traffic_modulators = []
        for n,d in self.graph.nodes_iter(data=True):
            if 'traffic' not in d:
                continue

            modulators = d['traffic'].split()
            if self.debug:
                print 'modulators',modulators
            for mkey in modulators:
                mkey = mkey.replace('"','')
                # Add by J.W. [2012-04-10 00:21:51]
                if not mkey:
                    print 'warning, one node has no modulator'
                    continue

                modspecstr = d[mkey].replace('"', '')

                if self.debug:
                    print 'configing mod',modspecstr
                m = self.__configure_traf_modulator(modspecstr, n, d)
                m.start()
                self.traffic_modulators.append(m)



    def __configure_traf_modulator(self, modstr, srcnode, xdict):
        modspeclist = modstr.split()
        moddict = {}
        for i in xrange(1,len(modspeclist)):
            # import pdb;pdb.set_trace()
            k,v = modspeclist[i].split('=')
            moddict[k] = v
            # print moddict[k]
            # print str(type(moddict[k]))

        if self.debug:
            print 'inside config_traf_mod',moddict

        assert('profile' in moddict or 'sustain' in moddict)

        trafprofname = moddict.get('generator', None)
        st = moddict.get('start', None)
        st = eval(st)
        if isinstance(st, (int, float)):
            st = randomchoice(st)

        profile = moddict.get('profile', None)
        if not profile:
            profile = moddict.get('sustain', None)

        emerge = moddict.get('emerge', None)
        withdraw = moddict.get('withdraw', None)

        # print 'trafprofname, ', trafprofname
        # import pdb;pdb.set_trace()
        assert (trafprofname in xdict)

        trafprofstr = xdict[trafprofname]
        trafprofstr = trafprofstr.replace('"','')
        if self.debug:
            print 'got profile',trafprofstr
        tgen = self.__configure_traf_spec(trafprofstr, srcnode, xdict)
        fm = FlowEventGenModulator(self, tgen, stime=st, emerge_profile=emerge, sustain_profile=profile, withdraw_profile=withdraw)
        if self.debug:
            print 'flow modulator',fm
        return fm


    def __configure_traf_spec(self, trafspec, srcnode, xdict):
        trafspeclist = trafspec.split()

        gen = None
        if trafspeclist[0] == 'rawflow' or trafspeclist[0] == 'simple':
            # configure really simple 'rawflow' traffic generator
            trafdict = mkdict(trafspeclist[1:])
            if self.debug:
                print 'simple trafdict to',srcnode,trafdict
            gen = lambda: SimpleGeneratorNode(self, srcnode, **trafdict)

        elif trafspeclist[0] == 'harpoon':
            # configure harpoon-style generator
            # configure really simple traffic generator
            trafdict = mkdict(trafspeclist[1:])
            if self.debug:
                print 'harpoon trafdict',srcnode, trafdict
            gen = lambda: HarpoonGeneratorNode(self, srcnode, **trafdict)

        elif trafspeclist[0] == 'subtractive':
            # configure subtractive anomaly
            trafdict = mkdict(trafspeclist[1:])
            if self.debug:
                print 'subtractive trafdict', srcnode, trafdict
            gen = lambda: SubtractiveGeneratorNode(self, srcnode, **trafdict)
        else:
            import pdb;pdb.set_trace()
            raise InvalidTrafficSpecification(trafspecstr)
        return gen


    def router(self, rname):
        '''
        get the router object corresponding to a name
        '''
        return self.routers[rname]


    def __linkdown(self, a, b, edict, ttf, ttr):
        '''
        kill a link & recompute routing
        '''
        self.logger.info('Link failed %s - %s' % (a,b))
        self.graph.remove_edge(a,b)
        self.__configure_routing()

        uptime = None
        try:
            uptime = next(ttr)
        except:
            self.logger.info('Link %s-%s permanently taken down (no recovery time remains in generator)' % (a, b))
            return
        else:
            self.after(uptime, 'link-recovery-'+a+'-'+b, self.__linkup, a, b, edict, ttf, ttr)


    def __linkup(self, a, b, edict, ttf, ttr):
        '''
        revive a link & recompute routing
        '''
        self.logger.info('Link recovered %s - %s' % (a,b))
        self.graph.add_edge(a,b,weight=edict.get('weight',1),delay=edict.get('delay',0),capacity=edict.get('capacity',1000000))

        # for k,v in edict.iteritems():
        #     self.graph[a][b][k] = v

        self.__configure_routing()

        downtime = None
        try:
            downtime = next(ttf)
        except:
            self.logger.info('Link %s-%s permanently going into service (no failure time remains in generator)' % (a, b))
            return
        else:
            self.after(downtime, 'link-failure-'+a+'-'+b, self.__linkdown, a, b, edict, ttf, ttr)


    def owd(self, a, b):
        '''
        get the raw one-way delay between a and b
        '''
        key = a + ':' + b
        rv = None
        if key in self.owdhash:
            rv = self.owdhash[key]
        return rv


    def delay(self, a, b):
        '''
        get the link delay between a and b
        '''
        d = self.graph[a][b]
        if d and 0 in d:
            return float(d[0]['delay'])
        return None


    def capacity(self, a, b):
        '''
        get the bandwidth between a and b
        '''
        d = self.graph[a][b]
        if d and 0 in d:
            return int(d[0]['capacity'])
        return None

    def nexthop(self, node, dest):
        '''
        return the next hop node for a given destination.
        node: current node
        dest: dest node name
        returns: next hop node name
        '''
        try:
            rlist = self.routing[node][dest]
        except:
            return None
        if len(rlist) == 1:
            return rlist[0]
        return rlist[1]

    def destnode(self, node, dest):
        '''
        return the destination node corresponding to a dest ip.
        node: current node
        dest: ipdest
        returns: destination node name
        '''
        # radix trie lpm lookup for destination IP prefix
        xnode = self.ipdestlpm.search_best(dest)

        if xnode:
            dlist = xnode.data['dests']
            best = None
            if len(dlist) > 1:
                # in the case that there are multiple egress nodes
                # for the same IP destination, choose the closest egress
                best = None
                bestw = 10e6
                for d in dlist:
                    w = dijkstra_path_length(self.graph, node, d)
                    if w < bestw:
                        bestw = w
                        best = d
            else:
                best = dlist[0]

            if self.debug:
                print 'destnode search',dest,dlist,best
            return best
        else:
            raise InvalidRoutingConfiguration('No route for ' + dest)


    def __start_routers(self):
        for rname,r in self.routers.iteritems():
            r.start()

    def run(self):
        self.__start_routers()

        simstart = self.__now
        self.simstart = simstart
        while (self.__now - simstart) < self.endtime and not self.intr:
            if len(self.heap) == 0:
                break
            expire_time,evid,fn,fnargs = heapq.heappop(self.heap)
            self.__now = expire_time
            if self.debug:
                print ("Event fires at {0}: {1}".format(self.now, evid))
            fn(*fnargs)

        if self.debug:
            print >>sys.stderr,'Reached simulation end time:',self.now,self.endtime

        print >>sys.stderr,'Reached simulation end time:',self.now,self.endtime
        for rname,r in self.routers.iteritems():
            r.shutdown()


    def stop(self):
        self.__stop_routers()
        self.done = True


class InvalidTrafficSpecification(Exception):
    pass


class Link(object):
    __slots__ = ['sim','capacity','delay','egress_node','ingress_node','backlog','bdp','queuealarm','lastalarm','alarminterval','doqdelay','logger']
    def __init__(self, sim, capacity, delay, ingress_node, egress_node):
        self.sim = sim
        self.capacity = capacity # bytes/sec
        self.delay = delay
        self.egress_node = egress_node
        self.ingress_node = ingress_node
        self.backlog = 0
        self.bdp = self.capacity * self.delay  # bytes
        self.queuealarm = 1.0
        self.lastalarm = -1
        self.alarminterval = 30
        self.doqdelay = True
        self.logger = logging.getLogger('flowmax')

    def decrbacklog(self, amt):
        self.backlog -= amt

    def flowlet_arrival(self, flowlet, prevnode, destnode):
        wait = self.delay + flowlet.size / self.capacity

        if self.doqdelay:
            queuedelay = max(0, (self.backlog - self.bdp) / self.capacity)
            wait += queuedelay
            self.backlog += flowlet.size
            if queuedelay > self.queuealarm and self.sim.now - self.lastalarm > self.alarminterval:
                self.lastalarm = self.sim.now
                self.logger.warn("Excessive backlog on link %s-%s (%f sec (%d bytes))" % (self.ingress_node.name, self.egress_node.name, queuedelay, self.backlog))
            self.sim.after(wait, 'link-decrbacklog-'+str(self.egress_node.name), self.decrbacklog, flowlet.size)

        self.sim.after(wait, 'link-flowarrival-'+str(self.egress_node.name), self.egress_node.flowlet_arrival, flowlet, prevnode, destnode)


# exported_flow_num = 0

class Router(object):
    __slots__ = ['name','sim','flow_table','link_table','maintenance_cycle','autoack','longflowtmo','flowinactivetmo','debug','logger','__flowsampling','__pktsampling','exporter','counters','snmpexportinterval','snmpexportfile','snmpexportfh','anoExporter']

    BYTECOUNT = 0
    PKTCOUNT = 1
    FLOWCOUNT = 2

    def __init__(self, name, sim, exportfn, maint_cycle=60.0, autoack=False, debug=False, snmpexportinterval=0, snmpexportfile=None):
        self.name = name
        self.sim = sim
        self.flow_table = {}
        self.link_table = {}
        self.maintenance_cycle = maint_cycle
        self.autoack = autoack
        #self.longflowtmo = 60
        #self.flowinactivetmo = 30
        self.longflowtmo = -1
        self.flowinactivetmo = -1
        self.debug = debug
        self.logger = logging.getLogger('flowmax')
        self.flowsampling = 1.0
        self.pktsampling = 1.0
        self.exporter = exportfn(self.name)
        self.counters = {}
        self.snmpexportinterval = snmpexportinterval
        self.snmpexportfile = snmpexportfile
        self.snmpexportfh = None

        if self.snmpexportinterval > 0:
            if self.snmpexportfile == 'stdout':
                self.snmpexportfh = sys.stdout
            else:
                snmpoutfile = str(self.name) + '_' + self.snmpexportfile + '.txt'
                self.snmpexportfh = open(snmpoutfile, 'w')

        self.anoExporter = exportfn('abnormal_' + self.name)

    def start(self):
        # start router maintenance loop at random within first 10 seconds
        # maintenance loop periodically fires thereafter
        # (below code is used to desynchronize router maintenance across net)
        self.sim.after(random.random()*self.maintenance_cycle, 'router-maintenance-'+str(self.name), self.router_maintenance)
        if self.snmpexportinterval > 0:
            self.sim.after(0, 'router-snmpexport-'+str(self.name), self.snmp_export)


    def add_link(self, link, next_router):
        self.link_table[next_router] = link

    def get_link(self, next_router):
        rv = None
        if next_router in self.link_table:
            rv = self.link_table[next_router]
        return rv

    @property
    def flowsampling(self):
        return self.__flowsampling

    @flowsampling.setter
    def flowsampling(self, fs):
        assert(0.0 < fs <= 1.0)
        self.__flowsampling = fs

    @property
    def pktsampling(self):
        return self.__pktsampling

    @pktsampling.setter
    def pktsampling(self, ps):
        assert(0.0 < ps <= 1.0)
        self.__pktsampling = ps

    def __store_flowlet(self, flowlet, prevnode):
        if self.flowsampling < 1.0:
            r = random.random()
            if r > self.flowsampling:
                return

        newflow = 0

        flet = None
        if flowlet.key in self.flow_table:
            flet = self.flow_table[flowlet.key]
            flet.flowend = self.sim.now
            flet += flowlet
        else:
            # NB: shallow copy of flowlet; will share same reference to
            # five tuple across the entire simulation
            newflow = 1
            flet = copy.copy(flowlet)
            flet.flowend += self.sim.now
            flet.flowstart = self.sim.now
            self.flow_table[flet.key] = flet
            flet.ingress_intf = prevnode

        counters = None
        if prevnode in self.counters:
            counters = self.counters[prevnode]
        else:
            counters = [0,0,0]
            self.counters[prevnode] = counters
        counters[Router.BYTECOUNT] += flowlet.bytes
        counters[Router.PKTCOUNT] += flowlet.pkts
        counters[Router.FLOWCOUNT] += newflow


    def __remove_flowlet(self, flowlet):
        if flowlet.key not in self.flow_table:
            return

        stored_flowlet = self.flow_table[flowlet.key]
        if stored_flowlet.flowend < 0:
            stored_flowlet.flowend = self.sim.now

        # Add By Jing Wang
        # print '_remove_flowlet'
        if stored_flowlet.anoFlag:
            # print 'Export Abnormal Flow'
            # print 'textexport %s %0.06f %s\n' % ('abnormal', self.sim.now, str(stored_flowlet))
            # global exported_flow_num
            # exported_flow_num += 1
            # print 'exported_flow_num, ', exported_flow_num
            self.anoExporter.exportflow(self.sim.now, stored_flowlet)
        # End Add By Jing Wang

        self.exporter.exportflow(self.sim.now, stored_flowlet)

        del self.flow_table[flowlet.key]

    def flowlet_arrival(self, flowlet, prevnode, destnode):
        if flowlet.xtype == 'subtractive':
            killlist = []
            ok = []
            for k,flet in self.flow_table.iteritems():
                if next(flowlet.xdata) and (not flowlet.srcaddr or flet.srcaddr in flowlet.srcaddr) and (not flowlet.dstaddr or flet.dstaddr in flowlet.dstaddr) and (not flowlet.ipproto or flet.ipproto == flowlet.ipproto):
                    killlist.append(k)
                else:
                    ok.append(k)
            for kkey in killlist:
                del self.flow_table[kkey]
            print 'subtractive flowlet encountered: removing',len(killlist),'keeping',len(ok),'me:',self.name,'dest',destnode,flowlet
            if destnode != self.name:
                nh = self.sim.nexthop(self.name, destnode)
                if nh:
                    egress_link = self.link_table[nh]
                    egress_link.flowlet_arrival(flowlet, self.name, destnode)
            return

        assert(flowlet.xtype == 'flowlet')
        self.__store_flowlet(flowlet, prevnode)

        # print 'flowlet_arrival',flowlet,'eof?',flowlet.endofflow
        if flowlet.endofflow:
            self.__remove_flowlet(flowlet)

        if destnode == self.name:
            if self.autoack and flowlet.ipproto == socket.IPPROTO_TCP and not flowlet.ackflow:
                revflow = Flowlet(flowlet.fivetuple.mkreverse())

                revflow.ackflow = True
                revflow.flowstart = revflow.flowend = self.sim.now

                if flowlet.tcpflags & 0x04: # RST
                    return

                if flowlet.tcpflags & 0x02: # SYN
                    revflow.tcpflags = revflow.tcpflags | 0x10
                    # print 'setting syn/ack flags',revflow.tcpflagsstr

                if flowlet.tcpflags & 0x01: # FIN
                    revflow.tcpflags = revflow.tcpflags | 0x10 # ack
                    revflow.tcpflags = revflow.tcpflags | 0x01 # fin

                revflow.pkts = flowlet.pkts / 2 # brain-dead ack-every-other
                revflow.bytes = revflow.pkts * 40

                self.__store_flowlet(revflow, self.name)

                # weird, but if reverse flow is short enough, it might only
                # stay in the flow cache for a very short period of time
                if revflow.endofflow:
                    self.__remove_flowlet(revflow)

                destnode = self.sim.destnode(self.name, revflow.dstaddr)

                # guard against case that we can't do the autoack due to
                # no "real" source (i.e., source was spoofed or source addr
                # has no route)
                if destnode and destnode != self.name:
                    nh = self.sim.nexthop(self.name, destnode)
                    if nh:
                        egress_link = self.link_table[nh]
                        egress_link.flowlet_arrival(revflow, self.name, destnode)
                    else:
                        self.logger.debug('No route from %s to %s (trying to run ackflow)' % (self.name, destnode))
        else:
            nh = self.sim.nexthop(self.name, destnode)
            assert (nh != self.name)
            if nh:
                egress_link = self.link_table[nh]
                egress_link.flowlet_arrival(flowlet, self.name, destnode)
            else:
                self.logger.debug('No route from %s to %s (in router nh decision; ignoring)' % (self.name, destnode))

    # def shutdown(self):
    #     killlist = []
    #     for k,v in self.flow_table.iteritems():
    #         if v.flowend < 0:
    #             v.flowend = self.sim.now
    #         self.exporter.exportflow(self.sim.now, v)
    #         killlist.append(k)

    #     for k in killlist:
    #         del self.flow_table[k]
    #     self.exporter.shutdown()
    #     if self.snmpexportfh and self.snmpexportfile != 'stdout':
    #         self.snmpexportfh.close()

    def shutdown(self):
        killlist = []
        t = []
        ft = []
        for k,v in self.flow_table.iteritems():
            t.append(v.flowstart)
            if v.flowend < 0:
                v.flowend = self.sim.now
            ft.append(v)
            killlist.append(k)
        idx = argsort(t)

        for i in idx:
            self.exporter.exportflow(self.sim.now, ft[i])
            if ft[i].anoFlag:
                 # print >>self.anoOutfile,'textexport %s %0.06f %s' % (self.name, self.sim.now, str(ft[i]))
                 import pdb;pdb.set_trace()
                 self.anoExporter.exportflow(self.sim.now, ft[i])


        for k in killlist:
            del self.flow_table[k]
        self.exporter.shutdown()
        self.anoExporter.shutdown()

        if self.snmpexportfh and self.snmpexportfile != 'stdout':
            self.snmpexportfh.close()




    def snmp_export(self):
        zeroedcounters = {}
        for k,v in self.counters.iteritems():
            # self.logger.info('snmp %s->%s %d bytes %d pkts %d flows' % (k, self.name, v[Router.BYTECOUNT], v[Router.PKTCOUNT], v[Router.FLOWCOUNT]))
            print >>self.snmpexportfh, '%8.3f %s->%s %d bytes %d pkts %d flows' % (self.sim.now, k, self.name, v[Router.BYTECOUNT], v[Router.PKTCOUNT], v[Router.FLOWCOUNT])
            zeroedcounters[k] = {Router.BYTECOUNT:0, Router.PKTCOUNT:0, Router.FLOWCOUNT:0}
        self.counters = zeroedcounters
        # self.counters = {}

        self.sim.after(self.snmpexportinterval, 'router-snmpexport-'+str(self.name), self.snmp_export)


    def router_maintenance(self):
        killlist = []
        for k,v in self.flow_table.iteritems():
            # if flow has been inactive for inactivetmo seconds, or
            # flow has been active longer than longflowtmo seconds, expire it
            if self.flowinactivetmo > 0 and ((self.sim.now - v.flowend) >= self.flowinactivetmo) and v.flowend > 0:
                if self.debug:
                    print 'flow inactive tmo',self.name,(self.sim.now-v.flowend),str(v)

                print '12'

                if v.anoFlag:
                    import pdb;pdb.set_trace()
                    self.anoExporter.exportflow(self.sim.now, v)
                self.exporter.exportflow(self.sim.now, v)
                killlist.append(k)

            if self.longflowtmo > 0 and ((self.sim.now - v.flowstart) >= self.longflowtmo) and v.flowend > 0:
                if self.debug:
                    print 'long flow tmo',self.name,(self.sim.now-v.flowstart),str(v)

                print 'AB'
                import pdb;pdb.set_trace()

                if v.anoFlag:
                    self.anoExporter.exportflow(self.sim.now, v)

                self.exporter.exportflow(self.sim.now, v)
                killlist.append(k)

        for k in killlist:
            if k in self.flow_table:
                del self.flow_table[k]

        # reschedule next router maintenance
        self.sim.after(self.maintenance_cycle, 'router-maintenance-'+str(self.name), self.router_maintenance)



def regression():
    exporter = text_export_factory
    sim = Simulator(0.05, 'i2.dot', exporter, debug=True, endtime=30)

    print 'houston->atl delay',sim.delay('houston', 'atlanta')
    print 'houston->atl capacity',sim.capacity('houston', 'atlanta')
    print 'next hop from ny to chicago',sim.nexthop('newyork','chicago')
    print 'next hop from kc to seattle',sim.nexthop('kansascity','seattle')
    print 'next hop from atlanta to losangeles',sim.nexthop('atlanta','losangeles')

    #dn = sim.destnode('newyork', '10.1.1.5')
    #print 'dest node from ny to 10.1.1.5 is',dn
    #print 'path from ny to',dn,'is:',
    #current = 'newyork'
    #while current != dn:
    #    nh = sim.nexthop(current, dn)
    #    print nh,
    #    current = nh
    #print

    print 'owd from ny to la:',sim.owd('newyork','losangeles')

    #gen = SimpleGeneratorNode(sim, 'newyork', ipaddr.IPAddress('10.1.1.5'), ipaddr.IPAddress('10.5.2.5'), 1)
    #sim.after(0.1, gen.start)
    #sim.run()


def main():
    parser = OptionParser()
    parser.prog = "flowmax.py"
    parser.add_option("-x", "--debug", dest="debug", default=False,
                      action="store_true", help="Turn on debugging output")
    parser.add_option("-t", "--simtime", dest="simtime", default=300, type=int,
                      help="Set amount of simulation time; default=300 sec")
    parser.add_option("-i", "--interval", dest="interval", default=1.0, type=float,
                      help="Set the simulation tick interval (sec); default=1 sec")
    parser.add_option("-s", "--snmpinterval", dest="snmpinterval", default=0.0, type=float,
                      help="Set the interval for dumping SNMP-like counters at each router (specify non-zero value to dump counters); default=no dump")
    parser.add_option("-S", "--snmpexportfile", dest="snmpexportfile", default=None,
                      help="Specify file for dumping SNMP-like counters (or 'stdout'); no default")
    parser.add_option("-e", "--exporter", dest="exporter", default="text",
                      help="Set the export type (text,cflow); default=text")
    parser.add_option("-z", "--usepsyco", action="store_true", default=False,
                      help="Use psyco for performance improvement; default=no psyco")
    (options, args) = parser.parse_args()

    if len(args) != 1:
        print >>sys.stderr,"Usage: %s [options] <scenario.dot>" % (sys.argv[0])
        sys.exit(0)

    scenario = args[0]

    exporter = None
    if options.exporter == 'text':
        exporter = text_export_factory
    elif options.exporter == 'cflow':
        exporter = cflowd_export_factory
    elif options.exporter == 'null':
        exporter = null_export_factory
    else:
        print >>sys.stderr, "Invalid export type.  Need 'text' or 'cflow'"
        sys.exit(0)

    sim = Simulator(options.interval, scenario, exporter, endtime=options.simtime, debug=options.debug, snmpexportinterval=options.snmpinterval, snmpexportfile=options.snmpexportfile)
    signal.signal(signal.SIGINT, sim.sighandler)

    if options.usepsyco:
        try:
            import psyco
            print >>sys.stderr, 'Starting psyco'
            # psyco.log()
            # psyco.profile(0.01)
            psyco.full()
            print >>sys.stderr, 'Done starting psyco'
        except ImportError:
            print >>sys.stderr, 'Sorry, no psyco'

    sim.run()

if __name__ == '__main__':
    # profile.run('main()', sort=1)
    # gc.set_debug(gc.DEBUG_STATS)
    main()
