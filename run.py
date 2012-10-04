#!/usr/bin/env python
from __future__ import print_function, division
import settings
import sys
sys.path.insert(0, settings.ROOT)

import argparse
import os

parser = argparse.ArgumentParser(description='sadit')
exper_ops = [f_name[:-3] for f_name in os.listdir('./Experiment/') if f_name.lower().endswith('py')]
parser.add_argument('-e', '--experiment', default='Experiment',
        help='specify the experiment name you want to execute. Experiments availiable are: %s. An integrated experiment will run fs-simulator first and use detector to detect the result.'%(exper_ops)
        )

parser.add_argument('-i', '--interpreter', default='python',
        help='--specify the interperter you want to use, now support [cpython], and [pypy](only for detector)')

parser.add_argument('-d', '--detect', default=None,
        help='--detect [filename] will simply detect the flow file, simulator will not run in this case, \
                detector will still use the configuration in the settings.py')

from Detector.API import detector_map, data_handler_handle_map, data_map
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

##################################
##   Enter Simple Detect Model  ##
##################################
from Detector import detect
from util import load_para
def pure_detect(args, res_args):
    default_settings = load_para(args.default_settigs)
    desc = default_settings['DETECTOR_DESC']
    if args.data_type:
        desc['data_type'] = args.data_type
    if args.feature_option:
        desc['fea_option'] = eval(args.feature_option)
    if args.method:
        desc['detector_type'] = args.method

    detector = detect(os.path.abspath(args.detect), desc, res_args)
    print('detector type, ', type(detector))
    if args.pic_show:
        print('--> plot the result')
    if args.pic_name:
        print('--> export result to %s'%(args.pic_name))

    detector.plot(pic_show=args.pic_show,
            pic_name=args.pic_name,
            hoeffding_false_alarm_rate=args.hoeff_far)

    if args.export_flows:
        print('--> export the abnormal flows')
        detector.export_abnormal_flow(args.export_flows,
                entropy_threshold = desc['entropy_threshold'],
                ab_win_portion = desc['ab_win_portion'],
                ab_win_num = desc['ab_win_num'],
                )

#######################################
##   Execture Integrated Experiments ##
#######################################
def exec_exper(args, res_args):
    os.chdir('./Experiment/')
    cmd = args.interpreter + ' ' + args.experiment + '.py ' + ' '.join(res_args)
    print('--> ', cmd)
    os.system(cmd)
    os.chdir('..')


def main(args, res_args):
    # try:
    if args.detect:
        pure_detect(args, res_args)
    else:
        if args.experiment not in exper_ops:
            raise Exception('invalid experiment')
        exec_exper(args, res_args)

    # except Exception as e:
        # print '--> [Exception]: ', e
        # parser.print_help()
        # exit()

if len(sys.argv) == 1:
    print('please use ./run.py -h to get help message')
    sys.exit()

args, res_args = parser.parse_known_args()
if args.profile:
    import cProfile
    command = """main(args, res_args)"""
    cProfile.runctx( command, globals(), locals(), filename=args.profile)
else:
    main(args, res_args)
