import copy
class AdaStoDetector(TwoWindowAnoDetector):

    def detect(self, data_file):
        self.data_file = data_file
        self.info = dict()
        # for win_size in [10, 50, 200, 400, 1000, 1500]:
        # for win_size in [10, 60, 200]:
        for win_size in [50, 100, 200, 500, 1000, 2000]:
            em_info = self.cal_em('time', win_size)
            adj_entro = self.cal_adj_entro(em_info['em'])
            self.info[win_size] = {'em_info':em_info, 'adj_entro':adj_entro}

    def cal_adj_entro(self, em):
        """calculate the cross entropy of two adjacent matrix
        """
        M = len(em)
        adj_entro = []
        for i in xrange(M-1):
            adj_entro.append( self.I(em[i], em[i+1]) )

        return adj_entro

    def plot(self, *args, **kwargs):
        # rt = self.record_data['winT']
        # plt.plot(rt[])
        # import pdb;pdb.set_trace()
        # plot_points(rt[0:-1], self.adj_entro,
                # *args, **kwargs)

        fig = plt.figure()
        mf_ax = fig.add_subplot(211)
        mb_ax = fig.add_subplot(212)
        # mf_fig = plt.figure()
        # mb_fig = plt.figure()
        for ws, info in self.info.iteritems():
            adj_entro = info['adj_entro']
            zip_ae = zip(*adj_entro)
            rt = info['em_info']['winT'][0:-1]
            # plt.plot(rt, zip_ae[0], figure=mf_fig)
            # plt.plot(rt, zip_ae[1], figure=mb_fig)
            mf_ax.plot(rt, zip_ae[0])
            mb_ax.plot(rt, zip_ae[1])
        leg = [str(v) for v in self.info.keys()]
        mf_ax.legend(leg)
        mb_ax.legend(leg)
        plt.savefig('adj_entro.pdf')
        plt.show()
        import pdb;pdb.set_trace()

    def cal_em(self, rg_type, win_size):
        self.record_data = dict(winT=[], em=[], rg=[])
        time = 0
        i = 0
        while True:
            i += 1
            if rg_type == 'time' : print 'time: %f' %(time)
            else: print 'flow: %s' %(time)

            try:
                self.rg = [time, time+win_size] # For two window method
                em = self.get_em(rg=[time, time+win_size], rg_type=rg_type)
                self.record( winT = time, em=em, rg=self.rg)
            except FetchNoDataException:
                print 'there is no data to detect in this window'
            except DataEndException:
                print 'reach data end, break'
                break

            time += win_size
        return copy.deepcopy(self.record_data)


