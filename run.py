#!/usr/bin/env python
from __future__ import print_function, division
import settings
import sys
sys.path.insert(0, settings.ROOT)

import argparse
import os
# import inspect

# Get experiment options
exper_ops = [f_name[:-3] for f_name in os.listdir('./Experiment/') if f_name.lower().endswith('py') and not f_name.startswith('__')]
# Get simple document for each experiment
help_doc = dict()
# try:
#     for exper in exper_ops:
#         exec('from Experiment import %s'%(exper))
#         help_doc[exper] = locals()[exper].__doc__ if locals()[exper].__doc__ else ''
# except Exception as e:
#     print('--> Exception [%s]. not all experiments can be imported, check them!!'%(e))
#     sys.exit()

from Detector.API import detector_map

# parser = argparse.ArgumentParser(description='sadit', add_help=False)
parser = argparse.ArgumentParser(description='sadit')
parser.add_argument('-e', '--experiment', default='DetectExper')
# parser.add_argument('-e', '--experiment', default=None)
parser.add_argument('--profile', default=None,
        help= """profile the program """)
parser.add_argument('-hm', '--help_method', default=None,
        help="""print the detailed help message for a method. Avaliable method [%s]"""
        %(' | '.join(detector_map.keys())))
parser.add_argument('-he', '--help_exper', default=None,
        help="""print the detailed help message for an experiment. Avaliable experiments are [%s]"""
        %(' | '.join(exper_ops)))

args, res_args = parser.parse_known_args()


if len(sys.argv) == 1:
    parser.print_help()
    sys.exit()
#     print("""please use ./run.py -e <exper> -h to get detailed help message for each experiment.
# Default value of <exper> is DetectExper, other options are \n * %s"""
# %('\n * '.join("[%s]: %s"%(exper, help_doc[exper])  for exper in exper_ops)))
#     sys.exit()


if args.help_exper:
#     print("""please use ./run.py -e <exper> -h to get detailed help message for each experiment.
# Default value of <exper> is DetectExper, other options are \n * %s"""
# %('\n * '.join("[%s]: %s"%(exper, help_doc[exper])  for exper in exper_ops)))
    exec('from Experiment.%s import %s'%(args.help_exper, args.help_exper))
    exper = locals()[args.help_exper](['-h'])
    sys.exit()

if args.help_method:
    from Detector.API import print_detector_help
    print_detector_help(args.help_method)
    sys.exit()

def main(args, res_args):
    if args.experiment not in exper_ops:
        raise Exception('invalid experiment')
        # exec_exper(args, res_args)
    exec('from Experiment.%s import %s'%(args.experiment, args.experiment))
    exper = locals()[args.experiment](res_args)
    exper.run()

if args.profile:
    import cProfile
    command = """main(args, res_args)"""
    cProfile.runctx( command, globals(), locals(), filename=args.profile)
else:
    main(args, res_args)
