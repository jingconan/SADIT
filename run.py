#!/usr/bin/env python
import argparse
import os
parser = argparse.ArgumentParser(description='sadit')
exper_ops = [f_name[:-3] for f_name in os.listdir('./Experiment/') if f_name.lower().endswith('py')]
parser.add_argument('-e', '--experiment', default='None',
        help='specify the experiment name you want to execute. Experiments availiable are: %s'%(exper_ops )
        )
parser.add_argument('-d', '--detect', default=None,
        help='--detect [filename] will simply detect the flow file, simulator will not run in this case')
args = parser.parse_args()

if args.detect:
    from Detector import standalone_detect
    standalone_detect(os.path.abspath(args.detect))
    exit()

try:
    if args.experiment not in exper_ops:
        raise Exception('invalid experiment')
except:
        parser.print_help()
        exit()

os.chdir('./Experiment/')
# print os.getcwd()
# execfile(args.experiment + '.py')
os.system('python ' + args.experiment + '.py' )
os.chdir('..')
