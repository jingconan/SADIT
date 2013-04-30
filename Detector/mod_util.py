""" Module level utility functions
"""
from __future__ import print_function, division, absolute_import
from sadit.util import plt

def find_seg(flag):
    """return (start and end point and level) of each segment"""
    n  = len(flag)
    start = [0]
    end = []
    tp = []
    for i in xrange(n-1):
        if flag[i+1] != flag[i]:
            start.append(i+1)
            # end.append(i+1) # to make lines continous
            end.append(i+2)
            tp.append(flag[i])
    end.append(n)
    tp.append(flag[n-1])
    return zip(start, end, tp)

def plot_seg(X, Y, flag, marker=None, *args, **kwargs):
    """plot X and Y, but the points with flag == true to be one color, the result to be another color
    """
    segs = find_seg(flag)
    for a, b, tp in segs:
        if marker[tp] is not None:
            plt.plot(X[a:b], Y[a:b], marker[tp], *args, **kwargs)

def plot_points(X, Y, threshold=None,  pic_show=False,
        pic_name=None, figure_=False, subplot_=111, title_ = None,
        xlabel_ = 'x', ylabel_ = 'y',
        ano_marker=['b-', 'r-'], threshold_marker='g--',
        xlim_=None, ylim_=None,
        *args, **kwargs):
    """ plot points and lines is a customized way for showing anomalies

    Parameters:
    ---------------
    X : list
        x coordinates
    Y : list
        Y coordinates
    threshold : list, optional
        threshold of detection result
    pic_show : bool, optional
        whether busy waiting and show picture
    pic_name : str, optional
        name of the output picture file
    figure_ : figure handle, optional
        figure handle in which this will be plotted.
    subplot_ : int, optional
        subplot id
    xlabel_, ylabel_, title_ : str, optional
        label for x axis and y axis and title of the figure
    ano_marker : list of str, optional
        ano_marker[0] is the marker for normal windows
        ano_marker[1] is the markov for abnormal windows
    threshold_marker : str, optional
        marker for threshold
    xlim_, ylim_ : list, optional
        range of x and y axies.

    Returns:
    --------------
    None

    """
    if not plt:
        return -1;
    if not figure_:
        figure_ = plt.figure()
    figure_.add_subplot(subplot_)

    if xlim_:
        plt.xlim(xlim_)
    if ylim_:
        plt.ylim(ylim_)

    if threshold is not None:
        ano_flag = [ (1 if e > th  else 0) for e, th in zip(Y, threshold)]
        plot_seg(X, Y, ano_flag, ano_marker, *args, **kwargs)
        if threshold_marker is not None:
            plt.plot(X, threshold, threshold_marker, *args, **kwargs)
    else:
        plt.plot(X, Y, ano_marker[0], *args, **kwargs)
    if title_:
        plt.title(title_)

    if pic_name: plt.savefig(pic_name)
    if pic_show: plt.show()


