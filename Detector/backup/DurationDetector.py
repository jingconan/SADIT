# --------- Revised For Considering Flow Duration Seperately --------
def ModelBased_Dur(gc, gd, gf, K, ND, NF, gr, NR):
    T = K * ND * NF * NR
    P = np.zeros( (T, T) )
    fl = len(gc)
    mp = np.zeros((T, ))
    for i in range(fl-1):
        m = gc[i] + gd[i] * K + gf[i] * K * ND + gr[i] * K * ND * NF
        mp[m] += 1
        n = gc[i+1] + gd[i+1] * K + gf[i+1] * K * ND + gr[i] * K * ND * NF
        P[m, n] += 1
    P = P * 1.0 / (fl-1)
    return P, mp

def ModelFree_Dur(gc, gd, gf, K, ND, NF, gr, NR):
    T = K * ND * NF * NR
    P = np.zeros( (T, ) )
    fl = len(gc)
    for i in range(fl):
        idx = gc[i] + gd[i] * K + gf[i] * K * ND + gr[i] * K * ND * NF
        P[idx] += 1
    P = P * 1.0 / fl
    assert(abs( np.sum(np.sum(P, 0)) - 1.0) < 0.01)
    return P

# ---------Start Detection Based On Duration ----
def Detect3(fName, clusterNum, ND, NF, wSize):
    '''Detect Using Flow Duration, not flow size and downloading rate'''
    # The Distance Function
    DF = lambda x,y:abs(x[0]-y[0]) * (256**3) + abs(x[1]-y[1]) * (256 **2) + abs(x[2]-y[2]) * 256 + abs(x[3]-y[3])

    # Generate Nominal PDF
    flow = ParseData(fName);
    srcIPVec, flowSize, t, dur = TransData(flow)
    cluster, centerPt = KMeans(srcIPVec, clusterNum, DF)
    distToCenter = GetDistToCenter(srcIPVec, cluster, centerPt, DF)
    distRange = [min(distToCenter), max(distToCenter)]
    flowSizeRange = [min(flowSize), max(flowSize)]
    durRange = [min(dur), max(dur)]


    normalStart = Find(t, 4000) + 1
    srcIPVec, flowSize, t, dur = TransData(flow[normalStart:])
    distToCenter = GetDistToCenter(srcIPVec, cluster, centerPt, DF)
    u, posDist = QuantizeState( distToCenter, ND, distRange)
    u, posFlowSize = QuantizeState( dur , NF, durRange)
    pmf = ModelFree(cluster, posDist, posFlowSize, clusterNum, ND, NF)
    Pmb, mpmb = ModelBased(cluster, posDist, posFlowSize, clusterNum, ND, NF)


    srcIPVec, flowSize, t, dur = TransData(flow)
    N = len(srcIPVec)

    minT = min(t)
    tRange = max(t) - minT
    print tRange
    t = [x-minT for x in t]

    IF = []
    IB = []

    winT = []
    # for i in range(0, N-wSize):
        # print 'time: ' + str(i)

    lp = 0 # last Position
    ti = 10 # Time Interval
    time = 0
    detectNum = int((max(t)-wSize )/ti)
    # print 't: ', t
    for i in range(detectNum):
        time += ti
        print 'time: %f' %(time)
        lp = Find(t, time)
        idx = Find(t, time+wSize)

        sIP = srcIPVec[lp:(idx+1)]
        fs = flowSize[lp:(idx+1)]
        duration = dur[lp:(idx+1)]
        if len(fs) == 0:
            continue
        # lp = idx+1
        # sIP = srcIPVec[i:(i+wSize)]
        # fs = flowSize[i:(i+wSize)]

        cluster, distToCenter = FindCenter(sIP, centerPt, DF) #FIXME
        u, posDist = QuantizeState( distToCenter, ND, distRange)
        u, posFlowSize = QuantizeState( duration, NF, durRange)
        d_pmf = ModelFree(cluster, posDist, posFlowSize, clusterNum, ND, NF)
        d_Pmb, d_mpmb = ModelBased(cluster, posDist, posFlowSize, clusterNum, ND, NF)
        mfEntro = I1(d_pmf, pmf)
        mbEntro = I2(d_Pmb, d_mpmb, Pmb, mpmb)
        IF.append(mfEntro)
        IB.append(mbEntro)
        winT.append(time)

    return IF, IB, winT
