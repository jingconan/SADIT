#!/usr/bin/env python
import argparse
import os
parser = argparse.ArgumentParser(description='sadit')
exper_ops = [f_name[:-3] for f_name in os.listdir('./Experiment/') if f_name.lower().endswith('py')]
parser.add_argument('-e', '--experiment', default='None',
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
        [%s]""" %(' | '.join(get_help_docs(detector_map)))
        )
# parser.add_argument('--data_handler', default=None,
#         help="""--specify the data handler you want to use, the availiable
#         option are: [%s] """ %(' | '.join(get_help_docs(data_handler_handle_map)))
#         )
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
parser.add_argument('--pic_name', default=None,
        help = """picture name for the detection result""")

args, res_args = parser.parse_known_args()

##################################
##   Enter Simple Detect Model  ##
##################################
if args.detect:
    from Detector import detect
    import settings
    desc = settings.DETECTOR_DESC
    # if args.data_handler: desc['data_handler'] = args.data_handler
    if args.data_type: desc['data_type'] = args.data_type
    if args.feature_option: desc['fea_option'] = eval(args.feature_option)
    if args.method: desc['detector_type'] = args.method
    detector = detect(os.path.abspath(args.detect), desc)
    print 'detector type, ', type(detector)

    if args.pic_name:
        detector.plot(pic_show=False, pic_name=args.pic_name)
    else:
        detector.plot()

    if args.export_flows:
        detector.export_abnormal_flow(args.export_flows,
                entropy_threshold = desc['entropy_threshold'],
                ab_win_portion = desc['ab_win_portion'],
                ab_win_num = desc['ab_win_num'],
                )
    exit()

#######################################
##   Execture Integrated Experiments ##
#######################################
try:
    print 'args.experiment', args.experiment
    if args.experiment not in exper_ops:
        raise Exception('invalid experiment')
except:
    parser.print_help()
    exit()

os.chdir('./Experiment/')
cmd = args.interpreter + ' ' + args.experiment + '.py ' + ' '.join(res_args)
print '--> ', cmd
os.system(cmd)
os.chdir('..')
