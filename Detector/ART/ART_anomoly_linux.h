#include <iostream>
#include <iomanip>
#include <fstream>
#include <vector>
#include <sstream>
#include <cstdlib>
#include <string>
#include <stdio.h>
#include <stdlib.h>
#include <cstring>
#include <math.h>
#include <time.h>
#include "ART_temporal_linux.h"
#include "ART_output_linux.h"

using namespace std;

void normalizeTime(vector<sample> &input)						//normalizes all start time and end times so that the earliest occurs at time 0
{
	double temp;
	int i = 0;

	temp = input[0].startTime;

	for(i = 1; i < input.size(); i++)			//finds earliest start time
	{
		if(input[i].startTime < temp)
			temp = input[i].startTime;
	}

	for(i = 0; i < input.size(); i++)				//make all times relative to the normalized start time
	{
		input[i].startTime = input[i].startTime - temp;
		input[i].endTime = input[i].endTime - temp;
	}
}

double absV(double num)
{
	if (num < 0.0)
	{
		num = num * -1;
		return num;
	}
	else
		return num;
}

float absV(float num)
{
	if (num < 0.0)
	{
		num = num * -1;
		return num;
	}
	else
		return num;
}

int absV(int num)
{
	if (num < 0)
	{
		num = num * -1;
		return num;
	}
	else
		return num;
}

double subtractTime(sample s, date lowest)
{
	double temp = 0;

	temp = (s.time.year - lowest.year) * 31104000 + (s.time.month - lowest.month) * 2592000 + (s.time.day - lowest.day) * 86400 + (s.time.hour - lowest.hour) * 3600;
	temp = temp + (s.time.min - lowest.min) * 60 + (s.time.sec - lowest.sec);

	return temp;
}

date firstTime(vector<sample> &input)				//finds the earliest date-time value in the entire input set
{
	int y, m, d, h, min, s;
	int i = 0;
	date temp;

	y = input[0].time.year;
	m = 13;
	d = 32;
	h = 25;
	min = 60;
	s = 60;

	for(i = 0; i < input.size(); i++)			//finds lowest year
	{
		if(input[i].time.year < y)
			y = input[i].time.year;
	}

	for(i = 0; i < input.size(); i++)			//finds lowest month within that year
	{
		if(input[i].time.year != y)
			continue;
		if(input[i].time.month < m)
			m = input[i].time.month;
	}

	for(i = 0; i < input.size(); i++)			//finds earliest day in the month
	{
		if(input[i].time.year != y)
			continue;
		if(input[i].time.month != m)
			continue;
		if(input[i].time.day < d)
			d = input[i].time.day;
	}

	for(i = 0; i < input.size(); i++)			//finds earliest hour
	{
		if(input[i].time.year != y)
			continue;
		if(input[i].time.month != m)
			continue;
		if(input[i].time.day != d)
			continue;
		if(input[i].time.hour < h)
			h = input[i].time.hour;
	}

	for(i = 0; i < input.size(); i++)			//finds earliest minute
	{
		if(input[i].time.year != y)
			continue;
		if(input[i].time.month != m)
			continue;
		if(input[i].time.day != d)
			continue;
		if(input[i].time.hour != h)
			continue;
		if(input[i].time.min < min)
			min = input[i].time.min;
	}

	for(i = 0; i < input.size(); i++)			//finds earliest second
	{
		if(input[i].time.year != y)
			continue;
		if(input[i].time.month != m)
			continue;
		if(input[i].time.day != d)
			continue;
		if(input[i].time.hour != h)
			continue;
		if(input[i].time.min != min)
			continue;
		if(input[i].time.sec < s)
			s = input[i].time.sec;
	}

	temp.year = y;
	temp.month = m;
	temp.day = d;
	temp.hour = h;
	temp.min = min;
	temp.sec = s;

	return temp;
}

void printHelp()
{
	cout << "\n\nInput options are as follows:\n\t-v1     Set vigilance paremeter for dim1 (0 to 1)";
	cout << "\n\t-v2     Set vigilance paremeter for dim2 (0 to 1)\n";
	cout << "\n\t-v3     Set vigilance paremeter for dim3 (0 to 1)\n";
	cout << "\n\t-i     Specifiy input filename\n";
	cout << "\n\t-th     Specifiy the threshold value\n";
	cout << "\n\t-h     Display this help";
}

void resetplus(vector<clusters> &cluster, sample a, int highC, float beta)			//used for initial cluster assignment
{
	cluster[highC].proto.bytes = (1-beta)*cluster[highC].proto.bytes + beta*a.bytes;
	cluster[highC].proto.ipDistance = (1-beta)*cluster[highC].proto.ipDistance + beta*a.ipDistance;
	cluster[highC].proto.deltaTime = (1-beta)*cluster[highC].proto.deltaTime + beta*a.deltaTime;
}

void resetplus2(vector<clusters> &cluster, sample a, int highC)						//used for fluctuations
{
	int num;
	float beta;

	num = cluster[highC].members.size();
	beta = 1/num;																		//the influence of each sample is proportional to the
	cluster[highC].proto.bytes = (1-beta)*cluster[highC].proto.bytes + beta*a.bytes;	//number of samples in the cluster
	cluster[highC].proto.ipDistance = (1-beta)*cluster[highC].proto.ipDistance + beta*a.ipDistance;
	cluster[highC].proto.deltaTime = (1-beta)*cluster[highC].proto.deltaTime + beta*a.deltaTime;
}

void resetminus(vector<clusters> &cluster, sample a, int highC)
{
	float delta1, delta2, delta3;
	int num;
	float beta;

	num = cluster[highC].members.size();									//the influence of each sample is proportional to the
	beta = 1/num;															//number of samples in the cluster

	delta1 = absV(cluster[highC].proto.bytes - a.bytes);			//difference between prototype and point on dimension 1
	delta2 = absV(cluster[highC].proto.ipDistance - a.ipDistance);		//difference between prototype and point on dimension 2
	delta3 = absV(cluster[highC].proto.deltaTime - a.deltaTime);		//difference between prototype and point on dimension 3

	if(cluster[highC].proto.bytes > a.bytes)								//always shift in the opposite direction of the sample
		cluster[highC].proto.bytes = (1-beta)*cluster[highC].proto.bytes + beta*delta1;	//from the perspective of the prototype vector
	else
		cluster[highC].proto.bytes = (1-beta)*cluster[highC].proto.bytes - beta*delta1;

	if(cluster[highC].proto.ipDistance > a.ipDistance)
		cluster[highC].proto.ipDistance = (1-beta)*cluster[highC].proto.ipDistance + beta*delta2;
	else
		cluster[highC].proto.ipDistance = (1-beta)*cluster[highC].proto.ipDistance - beta*delta2;

	if(cluster[highC].proto.deltaTime > a.deltaTime)
		cluster[highC].proto.deltaTime = (1-beta)*cluster[highC].proto.deltaTime + beta*delta3;
	else
		cluster[highC].proto.deltaTime = (1-beta)*cluster[highC].proto.deltaTime - beta*delta3;
}

void newCluster(vector<clusters> &cluster, sample a, int i, int id)		//creates a new cluster with the given sample
{
	clusters * temp;
	temp = new clusters;
	temp->members.push_back(i);
	temp->proto.bytes = a.bytes;
	temp->proto.packets = a.packets;
	temp->proto.ipDistance = a.ipDistance;
	temp->proto.deltaTime = a.deltaTime;
	temp->id = id;
	temp->anom = false;
	cluster.push_back(*temp);
}

double ipDistance(string one, string two)		//normalizes the difference between two ip addresses in a flow
{
	int a1, b1, c1, d1;
	int a2, b2, c2, d2;
	int first, last;
	string cc;
	first = last = 0;
	float a, b, c, d;
	double temp;

	last = one.find('.',first);			//parses ip addresses int four ints in the form a.b.c.d
	cc = one.substr(first,last-first);
	a1 = atoi(cc.c_str());
	first=last+1;

	last = one.find('.',first);
	cc = one.substr(first,last-first);
	b1 = atoi(cc.c_str());
	first=last+1;

	last = one.find('.',first);
	cc = one.substr(first,last-first);
	c1 = atoi(cc.c_str());
	first=last+1;

	last = one.find('.',first);
	cc = one.substr(first,last-first);
	d1 = atoi(cc.c_str());
	first=last+1;

	first = last = 0;
	last = two.find('.',first);
	cc = two.substr(first,last-first);
	a2 = atoi(cc.c_str());
	first=last+1;

	last = two.find('.',first);
	cc = two.substr(first,last-first);
	b2 = atoi(cc.c_str());
	first=last+1;

	last = two.find('.',first);
	cc = two.substr(first,last-first);
	c2 = atoi(cc.c_str());
	first=last+1;

	last = two.find('.',first);
	cc = two.substr(first,last-first);
	d2 = atoi(cc.c_str());
	first=last+1;

	a = absV(a1-a2);
	b = absV(b1-b2);
	c = absV(c1-c2);
	d = absV(d1-d2);

	temp = (a * pow(256.0,3.0)) + (b * pow(256.0,2.0)) + (c * 256) + d;

	return temp;
}

double similarity1(sample a, clusters &b)		
{
	double x1, x2;
	double y1, y2;
	double length1;
	double length2;
	double temp;
	double upper, lower;
	double PI = 3.14159;

	x1 = absV(a.ipDistance - b.proto.ipDistance);		//sample IP distance as a percentage of total range
	y1 = absV(a.bytes - b.proto.bytes);					//prototype IP distance as a percentage of total range

	x2 = x1 / b.proto.ipDistance;
	y2 = y1 / b.proto.bytes;

	temp = ((1 - x2) + (1 - y2)) / 2;

	if(temp < 0)
		return 0.001;
	else
		return temp;
}

double similarity2(sample a, clusters &b, sample high, sample low)		
{
	double x1, x2;
	double y1, y2;
	double length1;
	double length2;
	double temp;
	double upper, lower;
	double PI = 3.14159;

	high.ipDistance = ipDistance(high.sip, high.dip);
	low.ipDistance = ipDistance(low.sip, low.dip);

	x1 = (a.ipDistance - low.ipDistance) / (high.ipDistance - low.ipDistance) * 100;			//sample IP distance as a percentage of total range
	x2 = (b.proto.ipDistance - low.ipDistance) / (high.ipDistance - low.ipDistance) * 100;//prototype IP distance as a percentage of total range

	y1 = (a.bytes - low.bytes) / (high.bytes - low.bytes) * 100;				//sample bytes as a percentage of total range
	y2 = (b.proto.bytes - low.bytes) / (high.bytes - low.bytes) * 100;		//prototype bytes as a percentage of total range

	length1 = sqrt(x1 * x1 + y1 * y1);
	length2 = sqrt(x2 * x2 + y2 * y2);

	upper = x1 * x2 + y1 * y2;		//dot product
	lower = length1 * length2;

	temp = 1 - ((acos(upper/lower) * 180 / PI) / 90);		//normalizes angle difference to a value between zero and one

	return temp;
}

void addToCluster(vector<clusters> &cluster, int i, int bestMatch)			//add element i to cluster number highCluster
{
	cluster[bestMatch].members.push_back(i);
}

bool removeFromCluster(vector<clusters> &cluster, int i, int oldCluster)	//remove element i from cluster number highCluster
{
	int temp;
	int j = 0;
	temp = cluster[oldCluster].members.back();

	for(j = 0; j < cluster[oldCluster].members.size(); j++) //find the index where sample number i is stored
	{
		if (cluster[oldCluster].members[j] == i)
			break;
	}

	cluster[oldCluster].members[j] = temp; //overwrite index with last element
	cluster[oldCluster].members.pop_back(); //pop last element so there is not a duplicate
	
	if(cluster[oldCluster].members.empty())		//return true if empty so cluster can be removed
		return true;
	else
		return false;
}

float localize(sample a, clusters &b)
{
	float x1, x2, y1, y2, z1, z2;
	float length1, length2, length3;
	float delta1, delta2, delta3;
	float temp;

	x1 = a.ipDistance;
	x2 = b.proto.ipDistance;

	y1 = a.bytes;
	y2 = b.proto.bytes;

	z1 = a.deltaTime;
	z2 = b.proto.deltaTime;

	length1 = absV(x1 - x2);						//distance between sample point and prototype vector along dimension 1
	length2 = absV(y1 - y2);						//distance between sample point and prototype vector along dimension 2
	length3 = absV(z1 - z2);						//distance between sample point and prototype vector along dimension 3

	delta1 = length1 / x2;						//distance as a percentage of cluster prototype length
	delta2 = length2 / y2;						//along both dimensions
	delta3 = length3 / z2;

	temp = (delta1 + delta2 + delta3) / 3;				//average distance from prototype from all dimensions

	return (temp);
}

float localizeEuclid(sample a, clusters &b)
{
	float x1, x2, y1, y2, z1, z2;
	float length1, length2, length3;
	float delta1, delta2, delta3;
	float temp;

	x1 = a.ipDistance;
	x2 = b.proto.ipDistance;

	y1 = a.bytes;
	y2 = b.proto.bytes;

	z1 = a.deltaTime;
	z2 = b.proto.deltaTime;

	length1 = sqrt(absV(x1 - x2) * absV(x1 - x2) + absV(y1 - y2) * absV(y1 - y2) + absV(z1 - z2) * absV(z1 - z2));	//distance between sample point and prototype vector

	return length1;
}

void insert(vector<int> &c, float score, int cluster)
{
	int i;
	vector<int>::iterator it;
	if(c.empty())
	{
		c.push_back(cluster);
	}
	else
	{
		for(it = c.begin(); it < c.end(); it++)
		{
			if(score < *it)
			{
				c.insert(it, cluster);
				break;
			}
		}
		c.push_back(cluster);
	}
}

void removeCluster(vector<clusters> &cluster, int assigned, vector<sample> &input)
{
	clusters temp;
	int i = 0;
	temp = cluster.back();
	cluster[assigned] = temp;
	cluster.pop_back();
	for (i = 0; i < cluster[assigned].members.size(); i++)
	{
		input[cluster[assigned].members[i]].clusterAssigned = assigned;
	}
}

sample findHigh(vector<sample> &input)			//creates a sample with the highest value in all dimensions from all inputs
{
	sample temp;
	temp.bytes = input[0].bytes;
	temp.ipDistance = input[0].ipDistance;
	temp.deltaTime = input[0].deltaTime;
	
	int i = 0;

	for(i = 1; i < input.size(); i++)
	{
		if(input[i].bytes > temp.bytes)
			temp.bytes = input[i].bytes;
		if(input[i].ipDistance > temp.ipDistance)
			temp.ipDistance = input[i].ipDistance;
		if(input[i].deltaTime > temp.deltaTime)
			temp.deltaTime = input[i].deltaTime;
	}
	return temp;
}

sample findLow(vector<sample> &input)		//creates a sample with the lowest value in all dimensions from all inputs
{
	sample temp;
	temp.bytes = input[0].bytes;
	temp.ipDistance = input[0].ipDistance;
	temp.deltaTime = input[0].deltaTime;
	int i = 0;

	for(i = 1; i < input.size(); i++)
	{
		if(input[i].bytes < temp.bytes)
			temp.bytes = input[i].bytes;
		if(input[i].ipDistance < temp.ipDistance)
			temp.ipDistance = input[i].ipDistance;
		if(input[i].deltaTime < temp.deltaTime)
			temp.deltaTime = input[i].deltaTime;
	}
	return temp;
}

void idAnomolies(vector<clusters> &cluster, float threshold, vector<sample> &input, string output)
{
	int numClusters;
	float percentage;
	float t;
	int i;
	int samples;
	int totalAnom, totalAnomClusters;

	samples = input.size();
	totalAnomClusters = 0;
	totalAnom = 0;

	numClusters = cluster.size();
	percentage = threshold * samples / numClusters;
	t = ceil(percentage);		//this is the minimum number of samples a cluster must contain to not be an anomoly

	for(i = 0; i < numClusters; i++)
	{
		cluster[i].anom = false;
		if(cluster[i].members.size() < t)
		{
			cluster[i].anom = true;
			totalAnomClusters++;
			totalAnom = totalAnom + cluster[i].members.size();
			outputAnomoly(cluster[i], input, output);		//Outputs anomolies to file
		}
	}

	cout << "\n\nThere were " << totalAnom << " in " << totalAnomClusters << " clusters";
}

void randomize(vector<sample> &input)
{
	time_t seconds;
	int seed;
	int i;
	int s = input.size();
	int num;
	sample temp;

	seconds = time(NULL);
	seed = seconds % RAND_MAX;

	srand(seed);

	for(i = 0; i < s; i++)
	{
		num = rand() % s;
		temp = input[num];
		input[num] = input[i];
		input[i] = temp;
	}
}

bool localizeEllipse(sample a, clusters &b, float v1, float v2, float v3, float v4, int d, int radius, float range[])
{
	float x1, x2, y1, y2, z1, z2, a1, a2;
	float length1, length2, length3, length4;
	float delta1, delta2, delta3, delta4, delta5, delta6, delta7, delta8;
	float temp;
	float rx, ry, rz;

	x1 = a.ipDistance;
	x2 = b.proto.ipDistance;
	rx = range[0];

	y1 = a.bytes;
	y2 = b.proto.bytes;
	ry = range[1];

	z1 = a.deltaTime;
	z2 = b.proto.deltaTime;
	rz = range[2];

	if (d == 3)
	{
		delta1 = (x1-x2) * (x1-x2);
		delta2 = (y1-y2) * (y1-y2);
		delta5 = (z1-z2) * (z1-z2);
		delta3 = (rx * (1.0-v1)) * (rx * (1.0-v1));
		delta4 = (ry * (1.0-v2)) * (ry * (1.0-v2));
		delta6 = (rz * (1.0-v3)) * (rz * (1.0-v3));
		length1 = delta1 / delta3;		
		length2 = delta2 / delta4;
		length3 = delta5 / delta6;
		temp = length1 + length2 + length3;											//defines an ellipse around the prototype vector
	}

	if (d == 2)
	{
		delta1 = (x1-x2) * (x1-x2);
		delta2 = (y1-y2) * (y1-y2);
		delta3 = (rx * (1.0-v1)) * (rx * (1.0-v1));
		delta4 = (ry * (1.0-v2)) * (ry * (1.0-v2));
		length1 = delta1 / delta3;		
		length2 = delta2 / delta4;
		temp = length1 + length2;											//defines an ellipse around the prototype vector
	}

	if(temp < radius)
		return true;
	else
		return false;
}

