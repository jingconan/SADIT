
def FilterPt1stDigit(IPMat, val):
    '''Filter IP Address whose 1st Digits belongs to val'''
    [N, V] = np.shape(IPMat)
    assert( V==4 )
    assert ( type(val) == ListType )
    idx = []
    for i in range(N):
        ip = int(IPMat[i, 0])
        # print type(ip)
        # print type(val[0])
        # print ip
        if ip in val:
            idx.append(i)
    return idx



def FindFarPoint(IPMat, distance, DF):
    FirstByte = IPMat[:, 1]
    UFB = np.unique(FirstByte)
    if len(UFB) == 256:
        print 'the given ip occupy all spaces'
    print UFB
    print 'UFB: ' + str(len(UFB))
    return
# i = 0
#     while True:
#         candidate = np.random.randint(255, size=4)
#          print 'candidate: ' + str(candidate)
#          x,y = np.shape(IPMat)
#          flag = True
#          for i in range(x):
#              ip = IPMat[i, :]
#              if DF(candidate, ip) < distance:
#                  flag = False
#                  break
#          if flag:
#              return candidate
