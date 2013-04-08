# from StoDetector import DynamicStoDetector
import itertools
from StoDetector import *
from util import mkiter, meval, del_none_key
class EnsembleDetector(object):
    def __init__(self):
        self.det = dict()
        self.det_para = dict()
        self.det_type = dict()

    def register(self, alg_name, alg, para, type_ ='dynamic'):
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
        self.det_para[alg_name] = del_none_key(para)
        self.det_type[alg_name] = type_

    def call(self, alg_name, action, *args, **kwargs):
        pass

class RobustDetector(EnsembleDetector, FBAnoDetector):
    """ Robust Detector is designed for dynamic network environment
    """
    def __init__(self, desc):
        FBAnoDetector.__init__(self, desc)
        EnsembleDetector.__init__(self)

    # def init_parser(self, parser):
        # EnsembleDetector.init_parser(parser)
        # FBAnoDetector.init_parser(parser)
        # parser.add_argument('--start', default=0, type=float,
        #         help="""start point of the period selection""")

        # pass

    def detect(self, data_file):
        self.ref_pool = dict()

        self.register('mfmb', FBAnoDetector(self.desc), {}, 'static')
        # self.register('period', PeriodStoDetector(self.desc),
                # {'period':[1e3, 2e3]})
        self.register('speriod', PeriodStaticDetector(self.desc),
                # {'period':[1e3, 2e3, 3e3, 1e2, 5e2], 'start':[0, 100, 200]},
                {'period':[1e3, 2e3, 600, 200],
                    'start':[0, 150],
                    'delta_t':[100, 200]},
                'static')
        self.register('slowdrift', SlowDriftStaticDetector(self.desc),
                {}
                )
        # self.register('two_win', TwoWindowAnoDetector(self.desc),
        #         {'norm_win_ratio':[2, 10]})

        # self.process_history_data(data_file)
        FBAnoDetector.detect(self, data_file)

    def _loop_para(self, alg_name, history_file, int_rg):
        """ loop through the possible parameters for alg_name

        Parameters:
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
        d_obj.rg = int_rg
        d_obj.data_file = history_file

        para_dict = self.det_para[alg_name]
        for para_list in itertools.product(*para_dict.values()):
            cp = dict(zip(para_dict.keys(), para_list))
            key = (alg_name, str(cp))
            if self.det_type[alg_name] == 'static' and (self.ref_pool.get(key, None) is not None):
                continue
            else:
                self.ref_pool[key] = d_obj.cal_norm_em(norm_em=None, **cp)

    def process_history_data(self, history_file, int_rg=None):
        """ process history data using different methods and

        Parameters:
        ---------------------
        history_file: class
            data_handler class
        int_rg : list, optional
            Current range. It is helpful when the reference emperical measure
            is dependent on the detection place.

        Notes:
        ---------------------
            1. store the emperical measure calculated
            2. calculate the emtropy of each emperical measure

        """
        win_size = self.desc['win_size']
        if int_rg is None: int_rg = [0, win_size]

        # """specify the method and the parameters will be used"""
        for alg_name in self.det.keys():
            self._loop_para(alg_name, history_file, int_rg)


    def I(self, em, **kwargs):
        """ calculate

        Notes
        --------------------------
        Suppose we have emperical NE_i calcumated by detector i, i=1,...,N
        the output I = min(I(E, NE_i)) for i =1,...,N

        """
        self.process_history_data(self.data_file, int_rg = self.rg)

        d_pmf, d_Pmb, d_mpmb = em
        self.desc['em'] = em

        h_ref_size = len(self.ref_pool)
        I_rec = np.zeros((h_ref_size, 2))
        i = -1
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

        print 'I matrix: \n', I_rec
        print 'min entropy: \n', res
        print '--------------------'
        return res

