from __future__ import print_function, division
import os
import sys; sys.path.append("..")
import itertools
import time
import copy

def dict_sget(d, k):
    """ set dictionary according to a string

    Parameters:
    ---------------
    Returns:
    --------------
    examples
    --------------
    >>> d = {'a':{'b':[1.12]}}
    >>> print(dict_sget(d, 'a.b'))
    [1.12]
    """
    kl = k.rsplit('.')
    v = d
    for kv in kl:
        v = v.get(kv, {})
    return v

def dict_sset(d, k, v):
    """  set dictionary, according to k and v

    Parameters:
    ---------------
    d : dict
        dictionary
    k : string
        key
    v :
        value

    Returns:
    --------------
    None

    Examples
    --------------
    >>> d = {'a':{'b':[1]}}
    >>> dict_sset(d, 'a.b', [2])
    >>> print(d)
    {'a': {'b': [2]}}

    """
    kl = k.rsplit('.')
    struc = d
    for kv in kl[:-1]:
        struc = struc.get(kv, {})
    struc[kl[-1]] = v

def dict_supdate(d, d1):
    """

    Parameters:
    ---------------
    Returns:
    --------------

    Examples
    --------------
    >>> d = {'a':{'b':[1], 'c':[2]}}
    >>> dict_supdate(d, {'a.b':[3]})
    >>> print(d)
    {'a': {'c': [2], 'b': [3]}}
    """
    for k, v in d1.iteritems():
        dict_sset(d, k, v)


from BaseExper import BaseExper
class Batch(BaseExper):
    def __init__(self, exper, *args, **kwargs):
        self.exper = exper
        super(Batch, self).__init__(*args, **kwargs)
        self.desc = copy.deepcopy(self.args.config['DETECTOR_DESC'])
        self.batch_var_names = self.desc['batch_var']
        self.batch_var_vals = [dict_sget(self.desc, vn) \
                for vn in self.batch_var_names]

    def init_parser(self, parser):
        self.exper.init_parser(parser)
        parser.add_argument('--res_folder', default=None,
                help="""result folder name""")

    def export(self):
        raise Exception("abstract methdod")

    def run(self):
        RES_DIR = self.desc['res_folder']
        if not os.path.exists(RES_DIR):
            os.makedirs(RES_DIR)

        for cb in itertools.product(*self.batch_var_vals):
            print('run detection with combination: ')
            print('-' * 20)
            for tup in zip(self.batch_var_names, cb):
                print('%s: %s'%tup)
            print('-' * 20)
            start_time = time.clock()
            call_desc = copy.deepcopy(self.desc)
            dict_supdate(call_desc, dict(zip(self.batch_var_names, cb)))

            # run_here
            name = '-'.join([n+'_'+str(v) \
                    for n, v in zip(self.batch_var_names, cb)])
            self.export(RES_DIR+name, call_desc)

            end_time = time.clock()
            sim_dur = end_time - start_time
            print('Simulation Time [%d] seconds'%(sim_dur))

