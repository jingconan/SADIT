#!/usr/bin/env python
"""
Default Experimenet, will simply detect the flow file
"""
import argparse
import os
import settings
from Detector import detect
from util import load_para

class DetectExper(object):
    ROOT = settings.ROOT
    def __init__(self, argv, parser=None):
        if parser is None:
            parser = argparse.ArgumentParser()
        self.init_parser(parser)
        self.args, self.res_args = parser.parse_known_args(argv)

    def init_parser(self, parser):
        parser.add_argument('-d', '--detect', default=None,
                help='--detect [filename] will simply detect the flow file, simulator will not run in this case, \
                        detector will still use the configuration in the settings.py')

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

        # parser.add_argument('--hoeff_far', default=None, type=float,
        #         help= """hoeffding false alarm rate, useful in stochastic method""")

        parser.add_argument('--default_settings', default= settings.ROOT+ '/settings.py',
                help="""file_path for default settings, default value is the settings.py
                in ROOT directory""")

    def detect(self):
        args = self.args
        res_args = self.res_args
        default_settings = load_para(args.default_settings)
        desc = default_settings['DETECTOR_DESC']
        if args.data_type:
            desc['data_type'] = args.data_type
        if args.feature_option:
            desc['fea_option'] = eval(args.feature_option)
        if args.method:
            desc['detector_type'] = args.method

        detector = detect(os.path.abspath(args.detect), desc, res_args)
        self.detector = detector

        if args.export_flows:
            print('--> export the abnormal flows')
            detector.export_abnormal_flow(args.export_flows,
                    entropy_threshold = desc['entropy_threshold'],
                    ab_win_portion = desc['ab_win_portion'],
                    ab_win_num = desc['ab_win_num'],
                )
        return self.detector

    def run(self):
        args = self.args
        detector = self.detect()
        print('detector type, ', type(detector))

        if args.pic_show:
            print('--> plot the result')
        if args.pic_name:
            print('--> export result to %s'%(args.pic_name))

        detector.plot(pic_show=args.pic_show,
                pic_name=args.pic_name,
                )
                # far=args.hoeff_far)
