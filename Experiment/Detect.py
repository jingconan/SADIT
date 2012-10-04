#!/usr/bin/env python
import argparse
# import os
from Detector import detect
from util import load_para

class Detect(object):
    def __init__(self, argv, parser=None):
        if parser is None:
            parser = argparse.ArgumentParser()
        self.init_parser(parser)
        self.args, self.res_args = parser.parse_known_args(argv)
        self.settings = load_para(self.args.default_settings)

    def init_parser(self, parser):
        # exper_ops = [f_name[:-3] for f_name in os.listdir('./Experiment/') if f_name.lower().endswith('py')]
        # parser.add_argument('-e', '--experiment', default='Experiment',
        #         help='specify the experiment name you want to execute. Experiments availiable are: %s. An integrated experiment will run fs-simulator first and use detector to detect the result.'%(exper_ops)
        #         )

        # parser.add_argument('-i', '--interpreter', default='python',
        #         help='--specify the interperter you want to use, now support [cpython], and [pypy](only for detector)')

        # parser.add_argument('-d', '--detect', default=None,
        #         help='--detect [filename] will simply detect the flow file, simulator will not run in this case, \
        #                 detector will still use the configuration in the settings.py')

        from Detector.API import detector_map, data_map
        from util import get_help_docs
        parser.add_argument('-m', '--method', default=None,
                help="""--method [method] will specify the method to use. Avaliable options are:
                [%s]. If you want to compare the results of several methods, simple use / as seperator,
                for example [%s] """ %(' | '.join(get_help_docs(detector_map)), '/'.join(detector_map.keys()))
                )

        parser.add_argument('--data_type', default='fs',
                help="""--specify the type of the data you use, the availiable
                option are: [%s] """ %(' | '.join(get_help_docs(data_map)))
                )

        parser.add_argument('--feature_option', default=None,
                help = """ specify the feature option. feature option is a dictionary
                describing the quantization level for each feature. You need at least
                specify 'cluster' and 'dist_to_center'. Note that, the value of 'cluster' is the cluster number. The avaliability of other features depend on the data handler.
                """)

        parser.add_argument('--export_flows', default=None,
                help = """ specify the file name of exported abnormal flows. Default is not export
                """)
        parser.add_argument('--entropy_threshold', default=None,
                help = """ the threshold for entropy,
                """)
        parser.add_argument('--pic_name', default= settings.ROOT + '/res.eps',
                help = """picture name for the detection result""")

        parser.add_argument('--pic_show', default=False, action='store_true',
                help = """whether to show the picture after finishing running""")

        parser.add_argument('--profile', default=None,
                help= """profile the program """)

        parser.add_argument('--hoeff_far', default=None, type=float,
                help= """hoeffding false alarm rate, useful in stochastic method""")

        parser.add_argument('--default_settigs', default= settings.ROOT+ '/settings.py',
                help="""file_path for default settings, default value is the settings.py
                in ROOT directory""")

        pass

    # @property
    # def win_size(self): return self.settings.DETECTOR_DESC['win_size']
    # @property
    # def fea_option(self): return self.settings.DETECTOR_DESC['fea_option']
    # @property
    # def detector_type(self): return self.settings.DETECTOR_DESC['detector_type']
    # @property
    # def dot_file(self): return self.settings.OUTPUT_DOT_FILE
    # @property
    # def flow_file(self): return self.settings.ROOT + '/Simulator/n0_flow.txt'

    # @property
    # def ano_list(self): return self.settings.ANO_LIST
    # @property
    # def net_desc(self): return self.settings.NET_DESC
    # @property
    # def norm_desc(self): return self.settings.NORM_DESC

    # @net_desc.setter
    # def net_desc(self, v): self.settings.NET_DESC = v
    # @norm_desc.setter
    # def norm_desc(self, v): self.settings.NORM_DESC = v
    # @ano_list.setter
    # def ano_list(self, v): self.settings.ANO_LIST = v


    def detect(self):
        # return detect(self.flow_file, self.win_size, self.fea_option, self.detector_type, self.settings.DETECTOR_DESC)
        self.detector = detect(self.flow_file, self.settings.DETECTOR_DESC)
        return self.detector



    def run(self):
        self.configure()
        self.simulate()
        detector = self.detect()
        detector.plot_entropy(hoeffding_false_alarm_rate = 0.01)


class AttriChangeExper(Experiment):
    def __init__(self, settings):
        Experiment.__init__(self, settings)

if __name__ == "__main__":
    import settings
    exper = AttriChangeExper(settings)
    exper.configure()
    exper.simulate()
    detector = exper.detect()
    # detector.plot_entropy()
    detector.plot_entropy(hoeffding_false_alarm_rate = 0.01)

