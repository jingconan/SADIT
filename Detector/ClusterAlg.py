# from types import TupleType
'''
This module implement a typical K-means Clustering.
'''
from random import sample


def ReClustering(data, centerPt, DF):
	cluster = []
	for pt in data:
		dv = []
		for c in centerPt:
			d = DF(pt, c)
			dv.append(d)
		md = min(dv)
		cluster.append(dv.index(md))
	return cluster

def Add(x, y):
	res = []
	for i in range(len(x)):
		res.append(x[i]+y[i])

	return res

def NDivide(cSum, cLen):
	res = []
	for i in range(len(cSum)):
		x = []
		for j in range(len(cSum[0])):
			x.append( cSum[i][j] * 1.0 / cLen[i] )

		res.append(x)
	return res

def CalClusteringCenter(data, cluster):
	# print 'cluster: ' + str(cluster)
	ucLen = max(cluster) + 1
	cSum = []
	for i in range(ucLen):
		cSum.append([0]*len(data[0]))
	cLen = [0] * ucLen
	i = -1
	for ele in data:
		i += 1
		cl = cluster[i]
		# print 'cl: ' + str(cl)
		# print cSum
		cSum[cl] = Add(cSum[cl], ele)
		cLen[cl] += 1

	# print 'cSum: ' + str(cSum)
	try:
		cAve = NDivide(cSum, cLen)
	except:
		import pdb; pdb.set_trace()
	return cAve


def Equal(x, y):
	if len(x) != len(y):
		return False
	for i in range(len(x)):
		if x[i] != y[i]:
			return False
	return True

def KMeans(data, k, distFunc):
	# Initialize
	centerPt = sample(data, k)
	while True:
		cluster = ReClustering(data, centerPt, distFunc)
		NewCenterPt = CalClusteringCenter(data, cluster)
		if Equal(NewCenterPt, centerPt):
			break
		centerPt = NewCenterPt

	return cluster, centerPt
