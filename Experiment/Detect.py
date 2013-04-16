#!/usr/bin/env python
from __future__ import print_function, division, absolute_import
""" Default experimenet, will simply detect the flow data
"""
import os
import copy
from util import update_not_none
# import settings
from Detector import detect
from Detector.API import print_detector_help

# from util import update_not_none
# from util import load_para, update_not_none
# import copy
from .BaseExper import BaseExper

class Detect(BaseExper):
    def __init__(self, argv, parser=None):
        super(Detect, self).__init__(argv, parser)
        # BaseExper.__init__(self, argv, parser)

        self.desc = copy.deepcopy(self.args.config['DETECTOR_DESC'])
        update_not_none(self.desc, self.args.__dict__)

        # if self.args.help :
        if self.desc.get('help'):
            self.parser.print_help()
            if self.desc.get('method'):
                print_detector_help(self.desc.get('method'))


    def init_parser(self, parser):
        super(Detect, self).init_parser(parser)
        parser.add_argument('-h', '--help', default=False, action='store_true',
                help="""print help message""")

        parser.add_argument('-d', '--data', default=None,
                help="""--data [filename] will simply detect the flow file,
                simulator will not run in this case""")

        # parser.add_argument('-c', '--config', default=None,
        #         type=load_para,
        #         help="""config file with default arguments for detector""")

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

        parser.add_argument('--feature_option', default=None, type=eval,
                help = """ specify the feature option. feature option is a
                dictionary describing the quantization level for each feature.
                You need at least specify 'cluster' and 'dist_to_center'. Note
                that, the value of 'cluster' is the cluster number. The
                avaliability of other features depend on the data handler.
                """)

        parser.add_argument('--export_flows', default=None,
                help = """ specify the file name of exported abnormal flows. Default is not export
                """)
        # parser.add_argument('--entropy_threshold', default=None,
        #         help = """ the threshold for entropy,
        #         """)
        parser.add_argument('--pic_name', default= self.ROOT + '/res.eps',
                help = """picture name for the detection result""")

        parser.add_argument('--pic_show', default=False, action='store_true',
                help = """whether to show the picture after finishing running""")


        parser.add_argument('--csv', default=None,
                help = """the path of the file to save plots a text output""")

    def detect(self):
        # args = self.args
        # res_args = self.res_args
        # self.desc = copy.deepcopy(args.config['DETECTOR_DESC'])
        # update_not_none(self.desc, self.args.__dict__)
        # import ipdb;ipdb.set_trace()
        self.detector = detect(os.path.abspath(self.desc['data']), self.desc,
                self.res_args)
        return self.detector

    def run(self):
        detector = self.detect()
        desc = self.desc
        print('detector type, ', type(detector))

        # if args.export_flows:
        if desc['export_flows']:
            print('--> export the abnormal flows')
            detector.export_abnormal_flow(desc['export_flows'],
                    entropy_threshold = desc['entropy_threshold'],
                    ab_win_portion = desc['ab_win_portion'],
                    ab_win_num = desc['ab_win_num'],
                )
        if desc['pic_show']:
            print('--> plot the result')
        if desc['pic_name']:
            print('--> export result to %s'%(desc['pic_name']))

        detector.plot(pic_show=desc['pic_show'],
                pic_name=desc['pic_name'],
                csv=desc['csv'],
                )

        # if args.csv:
            # detector.save_plot_as_csv(args.csv)
                # far=args.hoeff_far)


# class DetectExper(Detect):
