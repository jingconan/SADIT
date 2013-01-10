# from StoDetector import DynamicStoDetector
from StoDetector import *
class RobustDetector(FBAnoDetector):
    """ Robust Detector is designed for dynamic network environment
    """
    def __init__(self, desc):
        """
        self.det are correspondence of detect id and class
        self.det_para_name is the correspondence of detector and parameters
        """
        super(RobustDetector, self).__init__(desc)
        self.det = {
                'period': PeriodStoDetector(desc),
                '2w': TwoWindowAnoDetector(desc),
                }

        """correspondence of the detector and the parameter name"""
        self.det_para_name = {
                'period':'period',
                '2w':'norm_win_ratio',
                'shift':'shift',
                }

    def init_parser(self, parser):
        pass

    def detect(self, data_file):
        self.ref_pool = dict()
        self.process_history_data(data_file)
        super(RobustDetector, self).detect(data_file)

    def process_history_data(self, history_file, int_rg=None, update_dets=None):
        """ process history data using different methods and
            1. store the emperical measure calculated
            2. calculate the emtropy of each emperical measure
        """
        win_size = self.desc['win_size']
        if update_dets is None: update_dets = self.det.keys()
        if int_rg is None: int_rg = [0, win_size]

        """specify the method and the parameters will be used"""
        data = {
                'period':[1e3, 2e3, 1.5e3, 3e3, 4e3],
                'norm_win_ratio':range(1, 10),
                }
        self.desc.update(data)

        for d_name in update_dets:
            d_obj = self.det[d_name]
            p_name = self.det_para_name[d_name]
            for val in self.desc.get(p_name, []):
                # d_obj.rg = [1e3, 1e3+win_size]
                d_obj.rg = int_rg
                d_obj.data_file = history_file
                self.ref_pool[(p_name, val)] = d_obj.cal_norm_em(**{p_name:val, 'norm_em':None})

    def I(self, em, **kwargs):
        """ Suppose we have emperical NE_i calcumated by detector i, i=1,...,N
        the output I = min(I(E, NE_i)) for i =1,...,N
        """
        self.process_history_data(self.data_file, int_rg=self.rg,
                update_dets=['2w'])
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
                continue

            pmf, Pmb, mpmb = norm_em
            I_rec[i, :] = [I1(d_pmf, pmf), I2(d_Pmb, d_mpmb, Pmb, mpmb)]

        print 'I_rec, ', I_rec
        res = np.min(I_rec, axis=0)
        print 'res, ', res
        return res

