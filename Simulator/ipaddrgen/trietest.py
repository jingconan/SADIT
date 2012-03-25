#
# Simple recipe for using the code.  Example uses the ipaddr
# module, but that isn't a requirement (just makes things
# nicer).
#

import ipaddr
import ipaddrgen

net = ipaddr.IPv4Network('127.0.0.0/8')
print int(net),net.prefixlen

t = ipaddrgen.initialize_trie(int(net), net.prefixlen, 0.61)
for i in xrange(10000):
    a = ipaddr.IPv4Address(ipaddrgen.generate_addressv4(t))
    print a

n = ipaddrgen.count_nodes(t)
print "nodes",n
ipaddrgen.release_trie(t)

