""" Robust Methods
"""
from __future__ import print_function, division, absolute_import
import itertools, copy
import cPickle as pk
from sadit.util import del_none_key, np

from . import StoDetector
from .DetectorLib import I1, I2
from .PLIdentify import PL_identify

def cal_I_rec(ref_pool, fb_PL, enable=None):
    """ calculate model-free and model-based fitness value with each reference
    PL in the pool

    Parameters
    ---------------
    ref_pool : dict
        a diction of (name, ref_PL)

    fb_PL : tuple
        model free and model based PL

    enable : list of list, optional
        enable[0][i] == True means the ith model-free referece PL

    Returns
    --------------
    I_rec : nx2 np.array
        n is the number of reference empirical measure
        the first column is the I1 and the second column is I2

    """
    d_pmf, d_Pmb = fb_PL

    n = len(ref_pool)
    if enable is None:
        enable = [[True] * n for i in [1, 2]]

    I_rec = np.zeros((n, 2))
    i = -1
    for _, ref_PL in ref_pool.iteritems():
        i += 1
        if ref_PL is None:
            I_rec[i, :] = [float('inf'), float('inf')]
            continue

        pmf, Pmb = ref_PL
        I_rec[i, 0] = I1(d_pmf, pmf) if enable[0][i] else float('inf')
        I_rec[i, 1] = I2(d_Pmb, Pmb) if enable[1][i] else float('inf')
    return I_rec

class PLManager(object):
    """ Probability Law Manager

    Parameters
    ---------------
        ref_file: data handler class
            data_handler class
    Returns
    --------------
    """

    def __init__(self, ref_file):
        self.ref_file = ref_file
        self.det = dict()
        self.det_para = dict()
        self.det_type = dict()
        self.det_flag = dict()

        self.ref_pool = dict()

    def register(self, alg_name, alg, para, type ='dynamic',
            para_type='izip'):
        """ register a algorithm

        Parameters
        --------------------
        alg_name : str
            name of the algorithm
        alg : a class object
            require *cal_norm_em* function.
        para : dict
            dict of all parameters. All the combinations
            of parameters will be tried
        type_ : {'static', 'dynamic'}
            'static' :
        para_type : {'izip', 'product'}
            define how to generate parameter combinations

        Returns
        --------------------
        None

        Notes
        --------------------

        """
        self.det[alg_name] = alg

        # store det_para
        para = del_none_key(para)
        self.det_para[alg_name] = (para.keys(), \
                getattr(itertools, para_type)(*para.values()))

        self.det_type[alg_name] = type

    def _loop_para(self, alg_name, int_rg):
        """ loop through the possible parameters for alg_name

        Parameters
        -------------------
            alg_name : str
                name of the algorithm
            int_rg : list
                range of data that will be used to calculated emperical measure

        Return
        -------------------
        None

        Notes
        -------------------
        the calculated empirical measure will be stored in a dictionary
        key is the (alg_name, para_str), where para_str is a str representing
        all the para combination.

        If the type of the algorithm is 'static', then the empirical measure
        will be only caculated for one time.

        """
        d_obj = self.det[alg_name]
        d_obj.rg = int_rg
        d_obj.ref_file = self.ref_file

        para_names, para_values_gen = self.det_para[alg_name]
        for para_values in para_values_gen:
            cp = dict(zip(para_names, para_values)) # parameters
            key = (alg_name, str(cp)) # key
            self.ref_pool[key] = d_obj.cal_norm_em(norm_em=None, **cp)

    def process_data(self, int_rg=None):
        """ process data using different methods and

        Parameters
        ---------------------

        int_rg : list, optional
            Current range. It is helpful when the reference emperical measure
            is dependent on the detection place.

        Notes
        ---------------------
            1. store the emperical measure calculated
            2. calculate the emtropy of each emperical measure

        """
        # win_size = self.desc['win_size']
        # if int_rg is None: int_rg = [0, win_size]

        # """specify the method and the parameters will be used"""
        for alg_name in self.det.keys():
            if self.det_type[alg_name] == 'static' and \
                self.det_flag.get(alg_name):
                    continue

            self.det_flag[alg_name] = True
            self._loop_para(alg_name, int_rg)

        return self.ref_pool

    def select(self, I_rec, lamb):
        n = len(I_rec) # window size
        m = I_rec[0].shape[0] # no. of PLs
        mf_D = np.zeros((m, n))
        mb_D = np.zeros((m, n))
        for j in xrange(n):
            for i in xrange(m):
                mf_D[i, j] = I_rec[j][i, 0]
                mb_D[i, j] = I_rec[j][i, 1]
        # import ipdb;ipdb.set_trace()
        return PL_identify(mf_D, lamb), PL_identify(mb_D, lamb)

class RobustDetector(StoDetector.FBAnoDetector):
    """ Robust Detector is designed for dynamic network environment
    """
    def __init__(self, desc):
        StoDetector.FBAnoDetector.__init__(self, desc)
        self._init_record()

    def _init_record(self):
        self.record_data = dict(entropy=[], winT=[], threshold=[], em=[])
        self.record_data['select_model'] = []
        self.record_data['I_rec'] = []

    def init_parser(self, parser):
        super(RobustDetector, self).init_parser(parser)
        parser.add_argument('--ref_scheck', default=None, type=str,
                help="""['dump', 'load']. whether to load the precomputed
                reference self check data or calculate and dump it""")

        parser.add_argument('--lamb', default=None, type=str,
                help="""upbound for nominal cross entropy, if lamb=0, disable
                Probability Law Identification""")

        # parser.add_argument('--ref_scheck_op', type=str,
                # help="""the reference data operation""")

    def detect(self, data_file, ref_file):
        register_info = self.desc['register_info']

        self.plm = PLManager(ref_file)

        for method, prop in register_info.iteritems():
            det = getattr(StoDetector, method)(copy.deepcopy(self.desc))
            self.plm.register(method, det, **prop)

        self.ref_pool = self.plm.process_data()

        #FIXME Need to clean these code later
        lamb = self.desc['lamb']
        self.PL_enable = None
        if lamb > 0: # enable Probability Law Identification
            rs_file = self.desc['dump_folder'] + '/PLManager_scheck.pk'
            if self.desc['ref_scheck'] == 'dump':
                StoDetector.FBAnoDetector.detect(self, ref_file, ref_file)
                ref_I_rec = self.record_data['I_rec']
                self.dump(rs_file)
                self._init_record()
            else:
                with open(rs_file, 'r') as f: data = pk.load(f)
                ref_I_rec = data['I_rec']

            self.PL_enable = self.plm.select(ref_I_rec, lamb)
            if self.PL_enable[0] is None or self.PL_enable[1] is None:
                raise Exception('lamb is too small')
        StoDetector.FBAnoDetector.detect(self, data_file, ref_file)

    def I(self, em, **kwargs):
        """ calculate

        Notes
        --------------------------
        Suppose we have emperical NE_i calcumated by detector i, i=1,...,N
        the output I = min(I(E, NE_i)) for i =1,...,N

        """
        # self.process_data(self.ref_file, self.rg)
        # self.ref_pool = self.plm.process_data(self.rg, self.PL_selection)

        d_pmf, d_Pmb= em
        self.desc['em'] = em

        I_rec = cal_I_rec(self.ref_pool, em, self.PL_enable)

        res = np.min(I_rec, axis=0)
        model = np.nanargmin(I_rec, axis=0)
        self.record_data['select_model'].append(model)
        self.record_data['I_rec'].append(I_rec)

        print('I matrix: \n', I_rec)
        print('min entropy: \n', res)
        print('model-free model: ', model[0], ' description: ',
                self.ref_pool.keys()[model[0]])
        print('model-based model: ', model[1], ' description: ',
                self.ref_pool.keys()[model[1]])
        print('--------------------')
        return res

    def save_addi_info(self, **kwargs):
        super(RobustDetector, self).save_addi_info()
        self.record_data['ref_pool'] = self.ref_pool
