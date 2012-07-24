##############################################
####    Utility Function for Configure #######
##############################################
def LoadValidIP(fileName):
    fid = open(fileName, 'r')
    content = fid.readline()
    # print content
    return content.split(',')

def GetIPAdress():
    '''
    Select normal IP address and abnormal IP address,
    the distance  between normal IP address and abnormal IP
    address is very large
    '''
    IPMat = GetIPMat() #  Get All IPs
    DF = lambda x,y:np.abs(x[0]-y[0])* (256 ** 3) + np.abs(x[1]- y[1]) * (256 ** 2) + np.abs(x[2] - y[2]) * (256) + np.abs(x[3] - y[3])
    # Calculate the center and distance to centers
    center, dis = CalIPCenter(IPMat, DF)
    sortIdx = np.argsort(dis, axis=0)
    ratio = 0.001 # Portion of selected points
    IPNum = len(dis)
    corePts = list( sortIdx[ range(int(IPNum * ratio)) ] );
    anoPts = list( sortIdx[ range(int(IPNum * (1-ratio)), IPNum, 1) ] )

    graphSize = len(corePts) + len(anoPts) # Size of the Graph

    IPSrcSet = []
    for pt in corePts:
        IPSrcSet.append("%d.%d.%d.%d" %(IPMat[pt, 0], IPMat[pt, 1], IPMat[pt, 2], IPMat[pt, 3]))
    AnoSet = []
    for pt in anoPts:
        AnoSet.append("%d.%d.%d.%d" %(IPMat[pt, 0], IPMat[pt, 1], IPMat[pt, 2], IPMat[pt, 3]))
    return IPSrcSet, AnoSet, graphSize

def CalIPCenter(IPMat, DF):
    '''*IPMat* is a Mx4 numpy matrix contains M ip addresses.
    *DF* is a user defined distance function'''
    IPNum, y = np.shape(IPMat)
    IPCenter = np.mean(IPMat, axis=0)
    dis = np.zeros( (IPNum, 1) )
    for i in range(IPNum):
        dis[i] = DF(IPMat[i,:], IPCenter)
    return IPCenter, dis


try:
    from matplotlib.pyplot import figure, plot
except:
    print 'no matplotlib'

def PlotPts(IPMat, corePts, anoPts, c):
    figure()
    for pt in corePts:
        plot(IPMat[pt, 0], IPMat[pt, 1], 'bo')
    for pt in anoPts:
        plot(IPMat[pt, 0], IPMat[pt, 1], 'ro')
    plot(c[0], c[1], 'go')

import settings
try:
    import numpy as np
except:
    print "numpy hasn't been installed"
def GetIPMat():
    '''load valid ip adrees from setting.IPS_FILE'''
    IP = LoadValidIP(settings.IPS_FILE)
    IPNum = len(IP)
    IPMat = np.zeros( (IPNum, 4) )
    i = -1
    for ip in IP:
        i += 1
        val = ip.split('.')
        ipInt = [int(x) for x in val]
        IPMat[i, :] = ipInt
    return IPMat

# def GetIPMat():
#     '''load valid ip adrees from setting.IPS_FILE'''
#     IP = LoadValidIP(settings.IPS_FILE)
#     return [ [int(x) for x in ip.split('.')] for ip in IP]




def P2F_RAW(flowRate, flowDuration, pktRate): # Change Prameter to FS Format for rawflow
    pass
# interval =
    # flowlets # Number of Flowlets in Flow
    # bytes # Number of Flowlets in each flow
    # interval # Interval between flowlets.
    # pkts # Number of packets in each emitted flow


# def F2P_RAW(flowlets, bytes, interval, pkts ):
#     pktRate = bytes * pkts / interval
#     flowDuration = flowlets * interval
#     flowRate = 1.0 / flowDuration



import re
def FixQuoteBug(fileName, delay=0.001):
    """ There is a bug in pydot. when link attribute is < 1, pydot will automatically add quote to value
    which is not desirable. This function try to fix that problem """
    fid = open(fileName, 'r')
    content = fid.read()
    content = re.sub('delay="[\d.]*"', 'delay='+str(delay), content)
    fid.close()
    fid = open(fileName, 'w')
    fid.write(content)
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
    '''Sub Class of String. __str__ method was overloaded, providing an easy way to
    get DOT format attribute string.'''
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
    n = len(ip_addr_set)
    return ip_addr_set[randint(0, n-1)]


import random

def RandDist(dist):
    '''Generate Random Variable According to Certain Kind of
    Distribution'''

    # TODO Finish A Complete Version
    s = 0
    rv = random.random()
    m = -1
    for p in dist:
        m += 1
        s += p
        if s > rv:
            break

    return m


