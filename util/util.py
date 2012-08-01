from random import randint

### -- [2012-03-04 12:12:42] add binary_search
### -- [2012-03-26 14:01:02] add docstring for each function.

def IN(*val_list):
    """Generate a string command that import object variables
    to locals() in the class methods"""
    return ";".join(['%s=self.%s'%(v, v) for v in val_list])

def OUT(*val_list):
    """Generate a string command that export object variables
    to locals() in the class methods"""
    return ";".join(['self.%s=%s'%(v, v) for v in val_list])

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
    if t == types.TupleType or t == types.ListType:
        return [Load(x) for x in var]
    elif t == types.DictType:
        res = dict()
        for k, v in var.iteritems():
            # If cannot properly loaded, use origianl value
            try:
                res[k] = Load(v)
            except Exception as e:
                res[k] = v
        return res
    elif t == types.StringType:
        return eval(var)
    elif t == types.FloatType or t == types.IntType:
        return var
    else:
        raise TypeError('unknown type of var')

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

try:
    import numpy as np
except ImportError:
    print 'no numpy'

def PrintVar(namespace, outputFile = ''):
    '''Print all variances in the namespace into .py file'''
    fid = -1
    if outputFile != '':
        fid = open(outputFile, 'w')
    import inspect
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


def abstract_method():
    """ This should be called when an abstract method is called that should have been
    implemented by a subclass. It should not be called in situations where no implementation
    (i.e. a 'pass' behavior) is acceptable. """
    raise NotImplementedError('Method not implemented!')

def FROM_CLS(*val_list):
    return ";".join(['%s=self.%s'%(v, v) for v in val_list])

def TO_CLS(*val_list):
    return ";".join(['self.%s=%s'%(v, v) for v in val_list])


class DataEndException(Exception):
    pass

class FetchNoDataException(Exception):
    pass



QUAN = 1
NOT_QUAN = 0

# The Distance Function
DF = lambda x,y:abs(x[0]-y[0]) * (256**3) + abs(x[1]-y[1]) * (256 **2) + abs(x[2]-y[2]) * 256 + abs(x[3]-y[3])

def zeros(s):
    if len(s) == 1:
        return [0] * s[0]
    elif len(s) == 2:
        return [[0 for i in xrange(s[1])] for j in xrange(s[0])]
    else:
        raise Exception('unknown size in zeros')


import inspect
def get_help_docs(dic):
    docs = []
    for k, v in dic.iteritems():
        doc  = inspect.getdoc(v)
        comp_doc = "%s %s"%(v.__name__, doc) if doc else v.__name__
        docs.append("'%s': %s"%(k, comp_doc))

    return docs
