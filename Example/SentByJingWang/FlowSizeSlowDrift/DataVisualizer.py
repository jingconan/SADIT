# ROOT = '/home/wangjing/Dropbox/Research/sadit'
ROOT = '/home/jzh/software/sadit'

import sys
sys.path.append(ROOT)
from Detector.Data import PreloadHardDiskFile
from Detector.DataHandler import QuantizeDataHandler
import numpy as np

fea_option = {'dist_to_center':5, 'flow_size':10, 'cluster':1}
# f_name = './n0_flow_reference.txt'
# f_name = './n0_flow_1_ano_200000_205000.txt'
f_name = './n0_flow_reference_steady_shift.txt'
data = PreloadHardDiskFile(f_name)
t = [v - data.min_time  for v in data.t]
dh = QuantizeDataHandler(data, dict(fea_option=fea_option))
start = np.arange(1, 6e5, 1.5*1e5)
delta_t = 1.5*1e5
# import ipdb;ipdb.set_trace()
import pylab
feas = dh.quantize_fea()
pylab.figure()
# import pdb;pdb.set_trace()
pylab.plot(t, feas[2])
pylab.show()
# for ss in start:
#     try:
#         print('delta_t', delta_t)
#         print('ss', ss)
#         feas = dh.quantize_fea([ss, ss+delta_t], 'time')
#         feas[2]
#         pylab.figure()
#         plot()
#     except:
#         print 'exception'
#         pass
