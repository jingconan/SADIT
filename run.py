#!/usr/bin/env python
from __future__ import print_function, division
import settings
import sys
sys.path.insert(0, settings.ROOT)

import argparse
import os

exper_ops = [f_name[:-3] for f_name in os.listdir('./Experiment/') if f_name.lower().endswith('py')]
if len(sys.argv) == 1:
    print("""please use ./run.py -e <exper> -h to get help message.
Default value of <exper> is DetectExper, other options are \n * %s"""%('\n * '.join(exper_ops)))
    sys.exit()

parser = argparse.ArgumentParser(description='sadit', add_help=False)
parser.add_argument('-e', '--experiment', default='DetectExper')
parser.add_argument('--profile', default=None,
        help= """profile the program """)
args, res_args = parser.parse_known_args()

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
