""" Robust Methods
"""
from __future__ import print_function, division, absolute_import
import itertools, copy
import numpy as np
from sadit.util import del_none_key

from . import StoDetector
# from .StoDetector import FBAnoDetector, FetchNoDataException, DataEndException
from .DetectorLib import I1, I2


class RobustDetector(StoDetector.FBAnoDetector):
    """ Robust Detector is designed for dynamic network environment
    """
    def __init__(self, desc):
        StoDetector.FBAnoDetector.__init__(self, desc)

        self.det = dict()
        self.det_para = dict()
        self.det_type = dict()

        self.record_data['select_model'] = []
        self.record_data['I_rec'] = []

    # def init_parser(self, parser):
        # pass

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

    def detect(self, data_file, ref_file):
        self.ref_pool = dict()

        register_info = self.desc['register_info']
        for method, prop in register_info.iteritems():
            # import ipdb;ipdb.set_trace()
            det = getattr(StoDetector, method)(copy.deepcopy(self.desc))
            # self.register(method, det, prop['para'], prop['type'])
            self.register(method, det, **prop)
            # globals()[method](copy.deepcopy(self.desc)),

        StoDetector.FBAnoDetector.detect(self, data_file, ref_file)

    def _loop_para(self, alg_name, ref_file, int_rg):
        """ loop through the possible parameters for alg_name

        Parameters
        -------------------
            alg_name : str
                name of the algorithm
            history_file : class
                data_handler class
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
        # d_obj.rg = int_rg
        d_obj.ref_file = ref_file

        # para_dict = self.det_para[alg_name]
        para_names, para_values_gen = self.det_para[alg_name]
        # for para_list in itertools.product(*para_dict.values()):
        # FIXME temparlily use izip
        for para_values in para_values_gen:
            cp = dict(zip(para_names, para_values))
            key = (alg_name, str(cp))
            if self.det_type[alg_name] == 'static' and \
                    (self.ref_pool.get(key, None) is not None):
                continue
            else:
                self.ref_pool[key] = d_obj.cal_norm_em(norm_em=None, **cp)

    def process_data(self, file_handler, int_rg=None):
        """ process data using different methods and

        Parameters
        ---------------------
        history_file : data handler class
            data_handler class
        int_rg : list, optional
            Current range. It is helpful when the reference emperical measure
            is dependent on the detection place.

        Notes
        ---------------------
            1. store the emperical measure calculated
            2. calculate the emtropy of each emperical measure

        """
        win_size = self.desc['win_size']
        if int_rg is None: int_rg = [0, win_size]

        # """specify the method and the parameters will be used"""
        for alg_name in self.det.keys():
            self._loop_para(alg_name, file_handler, int_rg)


    def I(self, em, **kwargs):
        """ calculate

        Notes
        --------------------------
        Suppose we have emperical NE_i calcumated by detector i, i=1,...,N
        the output I = min(I(E, NE_i)) for i =1,...,N

        """
        self.process_data(self.ref_file, self.rg)

        d_pmf, d_Pmb, d_mpmb = em
        self.desc['em'] = em

        h_ref_size = len(self.ref_pool)
        I_rec = np.zeros((h_ref_size, 2))
        i = -1
        # import ipdb;ipdb.set_trace()
        # calculate the model free and model based entropy for each referece
        # emperical measure
        for _, norm_em in self.ref_pool.iteritems():
            i += 1
            if norm_em is None:
                I_rec[i, :] = [float('inf'), float('inf')]
            else:
                pmf, Pmb, mpmb = norm_em
                I_rec[i, :] = [I1(d_pmf, pmf), I2(d_Pmb, d_mpmb, Pmb, mpmb)]

        res = np.min(I_rec, axis=0)
        model = np.nanargmin(I_rec, axis=0)
        # import ipdb;ipdb.set_trace()
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
