from __future__ import print_function, division, absolute_import
##############################################
####    Utility Function for Configure #######
##############################################
# import re
def FixQuoteBug(fileName):
    """ Fix A Quote related Bug Caused by `pydot`

    There is a bug in pydot. when link attribute is < 1, pydot will automatically add quote
    to value which is not desirable. This function try to fix that problem. delete
    all the quotes in the link attribute

    """
    with open(fileName, 'r') as fid:
        lines = fid.readlines()
    fid.close()
    for i in xrange(len(lines)):
        line = lines[i]
        if '--' in line: # if it is link attribute line
            newline = ''.join([c for c in line if c is not '"'])
            lines[i] = newline
    fid = open(fileName, 'w')
    fid.write(''.join(lines))
    fid.close()


def ParseArg(string):
    # print '---before--'
    # print string
    string = string.replace('"','')
    # print string
    # print '---after--'
    val = string.rsplit(' ')
    attr = dict()
    for v in val:
        sr = v.rsplit('=')
        if len(sr) == 1:
            attr['name'] = sr[0]
        else:
            x, y = sr
            attr[x] = y
    return attr

# Both Modulator and Source are described by Attr
class Attr():
    """ Attribute Class. Providing an easy way to get DOT format attribute string."""
    def __init__(self, string=None, **args):
        if not string:
            self.attr = args
        else:
            self.attr = ParseArg(string)

    def __str__(self):
        string = '"' + self.attr['name']
        for k, v in self.attr.iteritems():
            if k == 'name':
                continue
            string = string + ' ' + k + '=' + str(v).replace(" ", "")
        string = string + '"'
        return string


from random import randint
def choose_ip_addr(ip_addr_set):
    """ choose ip address """
    n = len(ip_addr_set)
    return ip_addr_set[randint(0, n-1)]


import random
def RandDist(dist):
    """ Generate Random Variable According to Certain Kind of Distribution

    Parameters
    ----------------
    dist : a list of floats
        the probability distribution

    Returns
    ---------------
    res : int
        an integer  0 <= res < len(dist). prob(res=i) = dist[i]

    """

    # TODO Use Binary Search Instead of Linear To Accelerate the program
    s = 0
    rv = random.random()
    m = -1
    for p in dist:
        m += 1
        s += p
        if s > rv:
            break

    return m


