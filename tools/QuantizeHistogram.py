from __future__ import print_function, division, absolute_import
import numpy as np
from sadit.Detector.DataHandler import QuantizeDataHandler
from sadit.Detector.Data import PreloadHardDiskFile

def identify_type(hist, bins, alpha1, alpha2):
    n = len(hist)
    nhist = np.array(hist) / np.sum(hist)
    print('alpha1', alpha1)
    s1 = int(n * alpha1)
    s2 = int(n * alpha2)

    # total = np.sum(hist)
    sum1 = np.sum(nhist[:s1])
    sum2 = np.sum(nhist[s1:s2])
    sum3 = np.sum(nhist[s2:])

    print('sum1', sum1)
    print('sum2', sum2)
    print('sum3', sum3)

    tp = "Period" if sum2 < sum3 else "SlowDrift"

    eps = 0.01
    slow_drift_range = np.nonzero(nhist < eps)[0][0]
    delta_t = bins[max(slow_drift_range, s1)]
    if tp == "Period":
        eps2 = 0.1
        seg3 = np.array(hist[s2:])
        maxs3 = np.max(seg3)
        nontrival_idx = np.nonzero(seg3 > eps2 * maxs3)[0]
        period = 2 * np.mean(bins[s2 + nontrival_idx])
        return tp, (delta_t, period)
    return tp, (delta_t,)


def merge_to_k(vals, K):
    """  reduce the element of a list to K by repeatedly merging the two
    floats that that closed to each other

    Parameters
    ---------------
    val : a list of floats
    K : int
        number of list after merging.

    Returns
    --------------
    res : a list of K floats

    Examples
    ---------------
    >>> merge_to_k([2, 3, 10], 2)
    [2.5, 10]
    """
    n = len(vals)
    for i in xrange(n-K):
        dif_val = np.diff(vals)
        amin = np.argmin(dif_val)
        new_vals = vals[:amin]
        mean = ( vals[amin] + vals[amin+1] ) / 2.0
        new_vals.append(mean)
        new_vals.extend(vals[(amin+2):])
        vals = new_vals

    return vals

def gen_register_info(pattern, t, K, SK=None):
    ri = {
            'PeriodStaticDetector' : {
                'type' : 'static',
                'para' : {
                    'start' : [],
                    'delta_t' : [],
                    'period':[],
                    },
                'para_type' : 'product',
                },
            'SlowDriftStaticDetector' : {
                'type' : 'static',
                'para' : {
                    'start' : [],
                    'delta_t' : [],
                    },
                'para_type' : 'product',
                },
            }

    p_delta_t = []
    p_period = []
    s_delta_t = []
    for tp, para in pattern:
        if tp == "Period":
            p_delta_t.append(para[0])
            p_period.append(para[1])
        elif tp == "SlowDrift":
            s_delta_t.append(para[0])

    rg = [min(t), max(t)]
    p_start = []
    # if len(p_period) > 0 or len(p_delta_t) > 0:
        # interval = SK if
        # p_start = np.arange(rg[0], max(p_period), max(p_delta_t)).tolist()
    p_start = np.linspace(rg[0], max(p_period), SK).tolist()

    p_delta_t = merge_to_k(p_delta_t, K)
    p_period = merge_to_k(p_period, K)
    # p_start = merge_to_k(p_start, SK)
    ri["PeriodStaticDetector"]['para']['delta_t'] = p_delta_t
    ri["PeriodStaticDetector"]['para']['period'] = p_period
    ri['PeriodStaticDetector']['para']['start'] = p_start


    # s_delta_t = ri['SlowDriftStaticDetector']['para']['delta_t']
    # s_start = []
    # if len(s_delta_t) > 0:
        # s_start = np.arange(rg[0], rg[1], max(s_delta_t)).tolist()
    s_start = np.linspace(rg[0], rg[1], SK).tolist()

    s_delta_t = merge_to_k(s_delta_t, K)
    # import ipdb;ipdb.set_trace()
    # s_start = merge_to_k(s_start, SK)

    ri['SlowDriftStaticDetector']['para']['delta_t'] = s_delta_t
    ri['SlowDriftStaticDetector']['para']['start'] = s_start

    return ri



def analyze_normal_pattern(t, qh, alpha1, alpha2):
    """  analyze normal pattern

    Parameters
    ---------------
    t : lisu
        start time of each flow
    qh : list of ints
        list of quantized state sequence.

    Returns
    --------------
    patterns : list of tuple
        each tuple is (tp, para), tp is the type of pattern. para is the
        parameters of the pattern

    """
    patterns = []
    for q in set(qh):
        idx = np.nonzero(np.array(qh) == q)[0]
        ti = t[idx]
        dti = np.diff(ti)
        hist, bins = np.histogram(dti, bins=30)
        centers = (bins[:-1]+bins[1:])/2
        tp, para = identify_type(hist, centers, alpha1, alpha2)
        patterns.append((tp, para))

    return gen_register_info(patterns, t, 3, 5)

def plot_histo_gram(t, qh):
    import matplotlib.pyplot as plt
    sfig = 420
    plt.figure()
    for q in set(qh):
        sfig += 1
        idx = np.nonzero(np.array(qh) == q)[0]
        ti = t[idx]
        dti = np.diff(ti)
        hist, bins = np.histogram(dti, bins=30)
        tp, time = identify_type(hist, 0.2, 0.5)
        print('time', time)
        print('tp', tp)
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

def main(f_name, desc, output):
    data = PreloadHardDiskFile(f_name)
    qa = QuantizeDataHandler(data, desc)
    qh = qa.hash_quantized_fea(None, None)
    print('len(qh): ', len(qh))

    t = data.t
    tmin = min(t)
    t = np.array([v - tmin for v in t])

    register_info = analyze_normal_pattern(t, qh, 0.1, 0.5)
    print('register_info', register_info)
    import json
    with open(output, 'w') as f:
      json.dump(register_info, f)

    return register_info

def cmd():
    import argparse
    parser = argparse.ArgumentParser(description='Analzye Normal Pattern')
    parser.add_argument('file', help='reference traffic file')
    parser.add_argument('output', help='output file name')
    args = parser.parse_args()

    desc = dict(
            fea_option = {'dist_to_center':1, 'flow_size':8, 'cluster':1},
            )
    main(args.file, desc, args.output)

if __name__ == "__main__":
    # cmd()
    desc = dict(
            fea_option = {'dist_to_center':1, 'flow_size':8, 'cluster':1},
            )

    main('../../CyberSecurity/Robust_Method/PaperSimulation/FlowSizePeriod/n0_referece_normal.txt',
        desc,
        './flowsize.json')
    # import doctest
    # doctest.testmod()






