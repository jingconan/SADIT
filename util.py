from random import randint

### -- [2012-03-04 12:12:42] add binary_search
### -- [2012-03-26 14:01:02] add docstring for each function.

def binary_search(a, x, lo=0, hi=None):
    """
    Find the index of largest value in a that is smaller than x.
    a is sorted Binary Search
    """
    # import pdb;pdb.set_trace()
    if hi is None: hi = len(a)
    while lo < hi:
        mid = (lo + hi) / 2
        midval = a[mid]
        if midval < x:
            lo = mid + 1
        elif midval > x:
            hi = mid
        else:
            return mid
    return hi-1

Find = binary_search

import types
def Load(var):
    '''Load is useful when the some elements in var is specified as random value.
    for example, if the var is ['rand(1)', 1], var[0] will be different random
    value at each time.'''
    t = type(var)
    # print 'type, ', t
    # print 'var, ', var
    if t == types.TupleType or t == types.ListType:
        return [eval(x) for x in var]
    elif t == types.DictType:
        res = dict()
        for k, v in var.iteritems():
            try: res[k] = eval(v)
            except: res[k] = v
        return res

def Dump2Txt(var, fname, op):
    """Dump2Txt will dump the variable to text file for use of other programs like Matlab.

    - *fname* : is the name for output file
    - *op* : is a option flag, ::

        if op[0:2] == '1d':
            m = len(var)
            for i in xrange(m): fid.write("%f "%(var[i]))
            fid.write('\\n')
        elif op[0:2] == '2d':
            if op[2:] == 'np': m, n = var.shape
            elif op[2:] == 'list':
                m = len(val)
                m = len(val[0])
            else:
                raise ValueError('unknown op')

            for i in xrange(m):
                for j in xrange(n):
                    fid.write("%s "%(var[i,j]))
                fid.write("\\n")


    """
    fid = open(fname, 'w')
    if op[0:2] == '1d':
        m = len(var)
        for i in xrange(m): fid.write("%f "%(var[i]))
        fid.write('\n')
    elif op[0:2] == '2d':
        if op[2:] == 'np': m, n = var.shape
        elif op[2:] == 'list':
            m = len(val)
            m = len(val[0])
        else:
            raise ValueError('unknown op')

        for i in xrange(m):
            for j in xrange(n):
                fid.write("%s "%(var[i,j]))
            fid.write("\n")
    else:
        raise ValueError('unknow op')

    fid.close()


import imp
def CreateSettings(templateFilePath, settingsFilePath, **kwargs):
    '''settings.py is a file contains all the global parameters.
    Sometimes we need to do the sensitivity analysis and need to change the global
    parameter on the fly. CreateSetting will faciliate the process through generating
    settings.py based on a template file.
    file.
    '''
    settings_template = imp.load_source('settings_template', templateFilePath)
    namespace = settings_template.__dict__
    for k, v in kwargs.iteritems():
        namespace[k] = v
    PrintVar(namespace, settingsFilePath)

import types
imports = 'types', 'sys', 'PrintVar', 'os', 'settings'

def PrintVar(namespace, outputFile = ''):
    '''Print all variances in the namespace into .py file'''
    fid = -1
    if outputFile != '':
        fid = open(outputFile, 'w')
    import inspect
    import numpy as np
    for k, v in namespace.iteritems():
        if k.startswith("__")==0 and k not in imports:
            # print 'type(v), ', type(v)
            if type(v) == types.StringType:
                expr ='%s = \'%s\'\n' %(k, str(v))
            elif type(v) == types.FunctionType:
                expr = inspect.getsource(v) + '\n'
                # removing the leading blankspace
                leadingSpace = expr.rfind('def')
                if leadingSpace != 0 and leadingSpace != -1:
                    srcLine = inspect.getsourcelines(v)
                    expr = ''
                    for line in srcLine[0]:
                        expr = expr + line[leadingSpace:]
                if leadingSpace != -1:
                    GetFuncName = lambda s: s[s.find('def')+4:s.find('(')]
                    funcName = GetFuncName(expr)
                    if funcName != k: expr += '\n%s = %s\n' %(k, funcName)

            elif type(v) == types.BuiltinFunctionType:
                module =inspect.getmodule(v)
                expr = 'from %s import %s\n' %(module.__name__,  v.__name__)
            elif type(v) == types.ModuleType:
                expr = 'import %s as %s\n' %(v.__name__, k)
            elif type(v) == np.ndarray:
                expr = k + ' = ' + str(v.tolist()) + '\n'
            else:
                expr = '%s = %s\n' %(k, str(v))
            if fid == -1:
                print expr,
                continue
            fid.write( expr )
    if fid != -1:
        fid.close()


import numpy as np
def PrintModelFree(mfIndi, mbIndi):
    '''Print the ModelFree Derivative which is not nan value'''
    # mfIndi = ModelFreeDetectAnoType()
    # mbIndi = ModelBaseDetectAnoType()
    for i in xrange(len(mfIndi)):
        if not np.isnan( mfIndi[i]):
            print '[%d]\t%f'%(i, mfIndi[i])
    print '\n'


def PrintModelBase(mbIndi):
    '''print the model based derivative which is not nan value.'''
    m, n = mbIndi.shape
    for i in xrange(m):
        for j in xrange(n):
            if not np.isnan(mbIndi[i,j]):
                print '[%d, %d]\t%f' %(i, j, mbIndi[i,j])
    print '\n'




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


def PlotPts(IPMat, corePts, anoPts, c):
    figure()
    for pt in corePts:
        plot(IPMat[pt, 0], IPMat[pt, 1], 'bo')
    for pt in anoPts:
        plot(IPMat[pt, 0], IPMat[pt, 1], 'ro')
    plot(c[0], c[1], 'go')

import settings
def GetIPMat():
    '''load valid ip adrees from setting.IPS_FILE'''
    # IP = LoadValidIP('./ips.txt')
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


def P2F_RAW(flowRate, flowDuration, pktRate): # Change Prameter to FS Format for rawflow
    pass
# interval =
    # flowlets # Number of Flowlets in Flow
    # bytes # Number of Flowlets in each flow
    # interval # Interval between flowlets.
    # pkts # Number of packets in each emitted flow


def F2P_RAW(flowlets, bytes, interval, pkts ):
    pktRate = bytes * pkts / interval
    flowDuration = flowlets * interval
    flowRate = 1.0 / flowDuration



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
