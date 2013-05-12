from __future__ import print_function, division, absolute_import
import numpy as np
from sadit.Detector.DataHandler import QuantizeDataHandler
from sadit.Detector.Data import PreloadHardDiskFile


desc = dict(
        fea_option = {'dist_to_center':1, 'flow_size':8, 'cluster':1},
        )

# f_name = '../../CyberSecurity/Robust_Method/PaperSimulation/FlowSizePeriod/n0_referece_normal.txt'
f_name = '../../CyberSecurity/Robust_Method/PaperSimulation/FlowSizeSlowDrift/n0_flow_reference.txt'
data = PreloadHardDiskFile(f_name)
qa = QuantizeDataHandler(data, desc)
qh = qa.hash_quantized_fea(None, None)
print('len(qh): ', len(qh))

t = data.t
tmin = min(t)
t = np.array([v - tmin for v in t])

import matplotlib.pyplot as plt
sfig = 420
plt.figure()
for q in set(qh):
    sfig += 1
    idx = np.nonzero(np.array(qh) == q)[0]
    ti = t[idx]
    dti = np.diff(ti)
    hist, bins = np.histogram(dti, bins=30)
    hist = hist[1:]
    bins = bins[1:]
    bins /= 3600
    # nhi = hi/np.sum(hist)
    width = 0.7*(bins[1]-bins[0])
    # plt.subplot(16, )
    plt.subplot(sfig)
    center = (bins[:-1]+bins[1:])/2
    plt.bar(center, hist, align = 'center', width = width)


plt.show()




