# from StoDetector import DynamicStoDetector
import itertools
from StoDetector import *
from util import mkiter, meval
def del_none_key(dt):
    """delete key whose value is None"""
    res = dict()
    for k, v in dt.iteritems():
        if v is not None:
            res[k] = v
    return res

class EnsembleDetector(object):
    def __init__(self):
        self.det = dict()
        self.det_para = dict()
        self.det_type = dict()

    def register(self, alg_name, alg, para, type_ ='dynamic'):
        """register a algorithm """
        self.det[alg_name] = alg
        self.det_para[alg_name] = del_none_key(para)
        self.det_type[alg_name] = type_

    def call(self, alg_name, action, *args, **kwargs):
        pass

# class StaticAdaptor(object):
#     """ To make Static Detectors (model free and model based methods)
#     to be called in the same way as DynamicStoDetector
#     Can also be used to make dynamic method static.
#     """
#     def __init__(self):
#         self.cache_norm_em = None

#     def cal_norm_em(self, **kwargs):
#         self.desc.update(kwargs)
#         if self.cache_norm_em is None:
#             self.cache_norm_em = self.static_action()
#         return self.cache_norm_em

# class RefDetector(FBAnoDetector, StaticAdaptor):
#     """To make FBAnoDetector to be called in the same way as
#     DynamicStoDetector
#     """
#     def __init__(self, desc):
#         FBAnoDetector.__init__(self, desc)
#         StaticAdaptor.__init__(self)

#     def static_action(self):
#         return FBAnoDetector.get_em(self,
#                 rg=self.desc['normal_rg'],
#                 rg_type=self.desc['win_type'])

class RefDetector(FBAnoDetector):
    """To make FBAnoDetector to be called in the same way as
    DynamicStoDetector
    """
    def cal_norm_em(self, **kwargs):
        return FBAnoDetector.get_em(self,
                rg=self.desc['normal_rg'],
                rg_type=self.desc['win_type'])

class PeriodStaticDetector(PeriodStoDetector):
    def init_parser(self, parser):
        super(PeriodStaticDetector, self).init_parser(parser)
        parser.add_argument('--start', default=0, type=float,
                help="""start point of the period selection""")

    def I(self, em, norm_em):
        d_pmf, d_Pmb, d_mpmb = em
        pmf, Pmb, mpmb = norm_em
        return I1(d_pmf, pmf), I2(d_Pmb, d_mpmb, Pmb, mpmb)

    def cal_norm_em(self, **kwargs):
        self.desc.update(kwargs)
        # import pdb;pdb.set_trace()
        nrg = [self.desc['start'],
                self.desc['start'] + self.desc['win_size']]
        return PeriodStoDetector.cal_norm_em(self, rg=nrg)

# class PeriodStaticDetector(PeriodStoDetector, StaticAdaptor):
#     """Make period stochastic detect static to accelerate
#     """
#     def __init__(self, desc):
#         PeriodStoDetector.__init__(self, desc)
#         StaticAdaptor.__init__(self)

#     def init_parser(self, parser):
#         PeriodStoDetector.init_parser(self, parser)
#         parser.add_argument('--start', default=0, type=float,
#                 help="""start point of the period selection""")

#     def cal_norm_em(self, **kwargs):
#         return StaticAdaptor.cal_norm_em(self, **kwargs)

#     def static_action(self):
#         nrg = [self.desc['start'],
#                 self.desc['start'] + self.desc['win_size']]
#         print 'nrg', nrg
#         import pdb;pdb.set_trace()
#         return PeriodStoDetector.cal_norm_em(self, rg=nrg)

class RobustDetector(EnsembleDetector, FBAnoDetector):
    """ Robust Detector is designed for dynamic network environment
    """
    def __init__(self, desc):
        FBAnoDetector.__init__(self, desc)
        EnsembleDetector.__init__(self)

    def init_parser(self, parser):
        pass
        # parser.add_argument('--two_win_nwr', default=None,
        #         type=lambda x:mkiter(meval(x)),
        #         help = """norm_win_ratio in TwoWindowAnoDetector""")
        # parser.add_argument('--period_period', default=None,
        #         type=lambda x:mkiter(meval(x)),
        #         help = """period parameter in PeriodStoDetector""")

    def detect(self, data_file):
        self.ref_pool = dict()

        # self.register('period', PeriodStoDetector(self.desc),
        #         {'period':self.args.period_period})
        # self.register('two_win', TwoWindowAnoDetector(self.desc),
        #         {'norm_win_ratio':self.args.two_win_nwr})

        self.register('ref', RefDetector(self.desc), {}, 'static')
        # self.register('period', PeriodStoDetector(self.desc),
                # {'period':[1e3, 2e3]})
        self.register('speriod', PeriodStaticDetector(self.desc),
                # {'period':[1e3, 2e3, 3e3, 1e2, 5e2], 'start':[0, 100, 200]},
                {'period':[1e3, 2e3, 1140], 'start':[0]},
                'static')
        # self.register('two_win', TwoWindowAnoDetector(self.desc),
                # {'norm_win_ratio':[4, 5]})

        # self.process_history_data(data_file)
        FBAnoDetector.detect(self, data_file)

    def loop_para(self, alg_name, history_file, int_rg):
        """ loop through the possible parameters for alg_name
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
            1. store the emperical measure calculated
            2. calculate the emtropy of each emperical measure

            - int_rg is the indicator for current range. It is helpful when
              the reference emperical measure is dependent on the detection
              place.
        """
        win_size = self.desc['win_size']
        if int_rg is None: int_rg = [0, win_size]

        # """specify the method and the parameters will be used"""
        # self.desc.update(data)
        # self.ref_pool = dict()
        for alg_name in self.det.keys():
            self.loop_para(alg_name, history_file, int_rg)


    def I(self, em, **kwargs):
        """ Suppose we have emperical NE_i calcumated by detector i, i=1,...,N
        the output I = min(I(E, NE_i)) for i =1,...,N
        """
        self.process_history_data(self.data_file, int_rg=self.rg)

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

        print 'I_rec, ', I_rec
        res = np.min(I_rec, axis=0)
        print 'min entropy, ', res
        return res

