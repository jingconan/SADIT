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
#include "ART_data_linux.h"

using namespace std;

int ajudicateY(vector<sample> &input, int index, long start, long end)
{
	int s = input.size();
	string key = input[index].sip;
	int i,j = 0;
	long bytes = 0;

	for(i = 0; i < s; i++)				//put all end time values for given IP into a vector
	{
		if(input[i].sip == key)
		{
			if((input[i].endTime > start) && input[i].endTime < end)		//the flow end time must fall in the necessary time interval
				bytes = bytes + input[i].bytes;
		}
	}
	return bytes;
}

vector<long> ajudicate(vector<sample> &input, int index, long start, long end)
{
	vector<long> times;
	int s = input.size();
	string key = input[index].sip;
	int i,j = 0;
	long low;

	for(i = 0; i < s; i++)				//put all end time values for given IP into a vector
	{
		if(input[i].sip == key)
		{
			if((input[i].endTime > start) && input[i].endTime < end)		//the flow end time must fall in the necessary time interval
				times.push_back(input[i].endTime);
		}
	}

	for(i = 0; i < times.size()-1; i++)		//sort the array from lowest to highest
	{
		low = times[i];
		index = i;
		for(j = i+1; j < times.size(); j++)
		{
			if(times[j] < low)
			{
				low = times[j];
				index = j;
			}
		}
		times[index] = times[i];
		times[i] = low;
	}
	return times;
}

int getFreq3(vector<sample> &input, int index)
{
	string s1, s2, key;
	size_t ind;
	int i = 0;
	int count = 0;

	s1 = input[index].sip;
	ind = s1.find_last_of('.');
	key = s1.substr(0,ind);

	for(i = 0; i < input.size(); i++)
	{
		s1 = input[i].sip;
		ind = s1.find_last_of('.');
		s2 = s1.substr(0,ind);
		if(key == s2)
			count++;
	}
	return count;
}

int getFreq2(vector<sample> &input, int index)
{
	string s1, s2, key;
	size_t ind, temp;
	int i = 0;
	int count = 0;

	s1 = input[index].sip;
	temp = s1.find_first_of('.');
	ind = s1.find('.', temp+1);
	key = s1.substr(0,ind);

	for(i = 0; i < input.size(); i++)
	{
		s1 = input[i].sip;
		temp = s1.find_first_of('.');
		ind = s1.find('.', temp+1);
		s2 = s1.substr(0,ind);
		if(key == s2)
			count++;
	}
	return count;
}

int getFreq1(vector<sample> &input, int index)
{
	string s1, s2, key;
	size_t ind;
	int i = 0;
	int count = 0;

	s1 = input[index].sip;
	ind = s1.find_first_of('.');
	key = s1.substr(0,ind);

	for(i = 0; i < input.size(); i++)
	{
		s1 = input[i].sip;
		ind = s1.find_first_of('.');
		s2 = s1.substr(0,ind);
		if(key == s2)
			count++;
	}
	return count;
}

void entropy(vector<clusters> &cluster, vector<sample> &input)
{
	float sum;
	sum = 0;
	int i, k, s;
	string a;
	s = input.size();					//total number of samples
	sample sam;
	i = 0;
	sum = 0;
	int duplicates;						//number of samples with multiple flows from source IP
	vector<sample> track;
	string filename = "c:\\data\\entropy.txt";
	int n, m, mi;
	float temp, temp2, max;
	ofstream file;

	//check full IP (4 octets)
	track.clear();
	i = 0;

	for(i = 0; i < s; i++)						//create a vector containing only multiple flows
	{
		if(input[i].freq > 1)
			track.push_back(input[i]);
	}

	i = 0;
	k = 0;
	for(i = 0; i < track.size(); i++)					//delete duplicates
	{
		a = track[i].sip;
		for(k = 0; k < track.size(); k++)
		{
			if(i == k)
				continue;
			if(track[k].sip == a)
			{
				sam = track.back();
				track[k] = sam;
				track.pop_back();
				k--;
			}
		}
	}

	m = input.size();
	sum = 0.0;

	for(i = 0; i < s; i++)
	{
		mi = input[i].freq;
		temp2 = (float)mi / (float)m;
		temp = (float)mi / (float)m * (log(temp2) / log(2.0));		//log base2 of x = log base 10 of x / log base 10 of 2
		sum = sum + temp;
	}

	sum = sum * -1;

	for(i = 0; i < track.size(); i++)
	{
		mi = track[i].freq;
		temp2 = (float)mi / (float)m;
		temp = (float)mi / (float)m * (log(temp2) / log(2.0));		//log base2 of x = log base 10 of x / log base 10 of 2
		sum = sum + (temp * (mi - 1));								//subtract out all but one of the rntropy calculations from multiple flows
	}

	max = log((float)m) / log(2.0);
	file.open(filename.c_str(), ios::app);
	file << "\n\nEntropy (4 Octets): " << sum << "\tPercentage : " << sum / max;
	file.close();

	//check 3 octets
	track.clear();
	i = 0;

	for(i = 0; i < s; i++)						//create a vector containing only multiple flows
	{
		input[i].freq = getFreq3(input, i);
		if(input[i].freq > 1)
			track.push_back(input[i]);
	}

	i = 0;
	k = 0;
	for(i = 0; i < track.size(); i++)					//delete duplicates
	{
		a = track[i].sip;
		for(k = 0; k < track.size(); k++)
		{
			if(i == k)
				continue;
			if(track[k].sip == a)
			{
				sam = track.back();
				track[k] = sam;
				track.pop_back();
				k--;
			}
		}
	}

	m = input.size();
	sum = 0.0;

	for(i = 0; i < s; i++)
	{
		mi = input[i].freq;
		temp2 = (float)mi / (float)m;
		temp = (float)mi / (float)m * (log(temp2) / log(2.0));		//log base2 of x = log base 10 of x / log base 10 of 2
		sum = sum + temp;
	}

	sum = sum * -1;

	for(i = 0; i < track.size(); i++)
	{
		mi = track[i].freq;
		temp2 = (float)mi / (float)m;
		temp = (float)mi / (float)m * (log(temp2) / log(2.0));		//log base2 of x = log base 10 of x / log base 10 of 2
		sum = sum + (temp * (mi - 1));								//subtract out all but one of the rntropy calculations from multiple flows
	}

	max = log((float)m) / log(2.0);
	file.open(filename.c_str(), ios::app);
	file << "\n\nEntropy (3 Octets) : " << sum << "\tPercentage : " << sum / max;
	file.close();
}

void entropy2(vector<clusters> &cluster, vector<sample> &input)
{
	float sum;
	sum = 0;
	int i, k, s;
	string a;
	s = input.size();					//total number of samples
	sample sam;
	i = 0;
	sum = 0;
	int duplicates;						//number of samples with multiple flows from source IP
	vector<sample> track;
	string filename = "c:\\data\\entropy.txt";
	int n, m, mi;
	float temp, temp2, max;
	ofstream file;

	//check IP (2 octets)
	track.clear();
	i = 0;

	for(i = 0; i < s; i++)						//create a vector containing only multiple flows
	{
		input[i].freq = getFreq2(input, i);
		if(input[i].freq > 1)
			track.push_back(input[i]);
	}

	i = 0;
	k = 0;
	for(i = 0; i < track.size(); i++)					//delete duplicates
	{
		a = track[i].sip;
		for(k = 0; k < track.size(); k++)
		{
			if(i == k)
				continue;
			if(track[k].sip == a)
			{
				sam = track.back();
				track[k] = sam;
				track.pop_back();
				k--;
			}
		}
	}

	m = input.size();
	sum = 0.0;

	for(i = 0; i < s; i++)
	{
		mi = input[i].freq;
		temp2 = (float)mi / (float)m;
		temp = (float)mi / (float)m * (log(temp2) / log(2.0));		//log base2 of x = log base 10 of x / log base 10 of 2
		sum = sum + temp;
	}

	sum = sum * -1;

	for(i = 0; i < track.size(); i++)
	{
		mi = track[i].freq;
		temp2 = (float)mi / (float)m;
		temp = (float)mi / (float)m * (log(temp2) / log(2.0));		//log base2 of x = log base 10 of x / log base 10 of 2
		sum = sum + (temp * (mi - 1));								//subtract out all but one of the rntropy calculations from multiple flows
	}

	max = log((float)m) / log(2.0);
	file.open(filename.c_str(), ios::app);
	file << "\n\nEntropy (2 Octets): " << sum << "\tPercentage : " << sum / max;
	file.close();

	//check 1 octets
	track.clear();
	i = 0;

	for(i = 0; i < s; i++)						//create a vector containing only multiple flows
	{
		input[i].freq = getFreq1(input, i);
		if(input[i].freq > 1)
			track.push_back(input[i]);
	}

	i = 0;
	k = 0;
	for(i = 0; i < track.size(); i++)					//delete duplicates
	{
		a = track[i].sip;
		for(k = 0; k < track.size(); k++)
		{
			if(i == k)
				continue;
			if(track[k].sip == a)
			{
				sam = track.back();
				track[k] = sam;
				track.pop_back();
				k--;
			}
		}
	}

	m = input.size();
	sum = 0.0;

	for(i = 0; i < s; i++)
	{
		mi = input[i].freq;
		temp2 = (float)mi / (float)m;
		temp = (float)mi / (float)m * (log(temp2) / log(2.0));		//log base2 of x = log base 10 of x / log base 10 of 2
		sum = sum + temp;
	}

	sum = sum * -1;

	for(i = 0; i < track.size(); i++)
	{
		mi = track[i].freq;
		temp2 = (float)mi / (float)m;
		temp = (float)mi / (float)m * (log(temp2) / log(2.0));		//log base2 of x = log base 10 of x / log base 10 of 2
		sum = sum + (temp * (mi - 1));								//subtract out all but one of the entropy calculations from multiple flows
	}

	max = log((float)m) / log(2.0);
	file.open(filename.c_str(), ios::app);
	file << "\n\nEntropy (1 Octets) : " << sum << "\tPercentage : " << sum / max;
	file.close();
}

int getFreq(vector<sample> &input, string ip)
{
	int size;
	int i = 0;
	int count = 0;
	size = input.size();

	for(i = 0; i < size; i++)
	{
		if(ip == input[i].sip)
			count++;
	}
	return count;
}