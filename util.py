from random import randint

### -- [2012-03-04 12:12:42] add binary_search

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


def Load(var):
    return [eval(x) for x in var]

def Dump2Txt(var, fname, op):
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
    # mfIndi = ModelFreeDetectAnoType()
    # mbIndi = ModelBaseDetectAnoType()
    for i in xrange(len(mfIndi)):
        if not np.isnan( mfIndi[i]):
            print '[%d]\t%f'%(i, mfIndi[i])
    print '\n'


def PrintModelBase(mbIndi):
    m, n = mbIndi.shape
    for i in xrange(m):
        for j in xrange(n):
            if not np.isnan(mbIndi[i,j]):
                print '[%d, %d]\t%f' %(i, j, mbIndi[i,j])
    print '\n'
