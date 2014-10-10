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
#include "ART_anomoly_linux.h"

using namespace std;

void analyze(vector<sample> &input, vector<clusters> &cluster, float beta, float v1, float v2, float v3, float v4, string colormap[], int dim, int radius, float range[])
{
	sample a, high, low;
	int i = 0;
	int j = 0;
	double highScore = 0;
	double temp;
	int highCluster = 0;
	int count;
	float complete;
	int numClusters = 1;
	ofstream file;
	int k = 0;
	string filename;
	char *t1, *t2;
	t1 = new char[1];
	t2 = new char[1];
	float r, g, b;
	float localScore;
	int n;
	
	cluster[0].members.pop_back();				//destroy place holder cluster information
	cluster[0].members.push_back(0);			//assign the first input element to the first cluster
	cluster[0].proto.bytes = input[0].bytes;
	cluster[0].proto.deltaTime = input[0].deltaTime;
	cluster[0].id = 1;							//index 0 contains the first cluster
	cluster[0].timeData.push_back(1);
	cluster[0].proto.ipDistance = ipDistance(input[0].sip, input[0].dip);
	cluster[0].anom = false;
	input[0].clusterAssigned = 0;
	
	cout << "\n\nAssigning samples to initial clusters";
	count = input.size();
	
	for(i = 1; i < count; i++)			//start comparison and assignmnet for second input onward
	{
		highScore = 0;
		highCluster = -1;
		
		a = input[i];
		highScore = localizeEuclid(a, cluster[0]);
		for(j = 0; j < cluster.size(); j++)	//iterate through each cluster
		{	
				localScore = localizeEuclid(a, cluster[j]);	
				if((localScore < highScore) || (localScore == highScore))		//if sample closer to the current cluster, it becomes new candidate
				{
					if(localizeEllipse(a, cluster[j], v1, v2, v3, v4, dim, radius, range))
					{
						highScore = localScore;
						highCluster = j;
					}
				}
		}

		if(highCluster != -1)
		{
			addToCluster(cluster, i, highCluster);
			input[i].clusterAssigned = highCluster;
			resetplus(cluster, a, highCluster, beta);
		}
		else		//no good cluster found, so create a new one
		{
			numClusters++;
			newCluster(cluster, a, i, numClusters);
			input[i].clusterAssigned = cluster.size() - 1;
			for(k = 0; k < i; k++)			//need to add zeroes for time data from 0 to i
				cluster[numClusters-1].timeData.push_back(0);
		}

		for(k = 0; k < cluster.size(); k++)	//iterate through each cluster and add time data
		{
			cluster[k].timeData.push_back(cluster[k].members.size());
		}

	}
}

int fluctuate(vector<sample> &input, vector<clusters> &cluster, float beta, float v1, float v2, float v3, float v4, int count, string colormap[], int dim, int radius, float range[])
{
	int flux = 0;		//flux is the number of samples that change clusters per each iteration
	int i = 0;			//count is the total number of iterations (or calls to the fluctuate function)
	int j = 0;
	int k = 0;
	int index, n;
	float score;
	float bestMatch;
	sample temp, high, low;
	bool empty;
	int oldCluster;
	int numClusters = cluster.size();
	ofstream file;
	string filename;
	int t;
	char *t1, *t2;
	t1 = new char[1];
	t2 = new char[1];
	float r, g, b;
	r = g = b = 0.0;
	int size;
	
	if (count == 1)
	{	
		for(i = 0; i < numClusters; i++)			//populate initial size for all clusters
		{
			t = cluster[i].members.size();
			cluster[i].timeData.push_back(t);
		}
	}

	for(i = 0; i < input.size(); i++)			//iterate through all samples
	{
		score = 0;
		temp = input[i];
		bestMatch = input[i].clusterAssigned;
		for(j = 0; j < cluster.size(); j++)		//compare to each existing cluster
		{	
			
			if(localize(temp, cluster[j]) > score)	//check if score is greater than current
			{	
				score = localize(temp, cluster[j]); //new high score for this input
				if (localizeEllipse(temp, cluster[j], v1, v2, v3, v4, dim, radius, range))			//score must pass gamma value and vigilance
					bestMatch = j;
			}
		}

		if (bestMatch != (temp.clusterAssigned))	//if highest score is currently assigned cluster then do nothing
			{
					addToCluster(cluster, i, bestMatch);		//else add to new cluster and remove from old
					resetplus2(cluster, temp, bestMatch);
					empty = removeFromCluster(cluster, i, temp.clusterAssigned);
					flux++;
					oldCluster = temp.clusterAssigned;
					input[i].clusterAssigned = bestMatch;
					if(!empty)
						resetminus(cluster, temp, oldCluster);
					if(empty)
					{	
						if(oldCluster == (cluster.size() - 1))
							cluster.pop_back();
						else
							removeCluster(cluster, oldCluster, input);
						numClusters--;
					}
			}
		
		for(k = 0; k < numClusters; k++)	//iterate through each cluster and add time data
		{
			cluster[k].timeData.push_back(cluster[k].members.size());
		}
	}

	size = input.size();	
return flux;
}

int main(int argc, char* argv[])
{
	string input;
	vector<sample> inputdata;
	vector<sample> newinput;
	vector<clusters> cluster;
	clusters initial;
	sample *temp;
	sample *temp2;
	ifstream file;
	int first = 0;
	int last = 0;
	int i = 0;
	char * cstr;
	string conversion;
	int count = 0;
	int fluctuations = 0;
	int samples = 0;
	parameters par;
	vector<int> flux;
	string colormap[26];
	int numSamples;
	int numSamples2;
	int iterations, iterations2;
	int initClusters;
	int fluxClusters;
	bool phaseTwo = false;
	bool timeHour = false;
	bool timeDay = false;
	bool temporal = false;
	int ns;
	string line, line2;
	string value;
	char abc;
	sample high, low;
	float range[3];
	date lowest;

	initial.proto.bytes = 0;						//populate initial cluster with empty values
	initial.proto.packets = 0;
	initial.proto.sip = "0";
	initial.proto.dip = "0";
	initial.proto.deltaTime = 0;
	initial.members.push_back(0);				//the zeroth member is a place holder for the cluster
	cluster.push_back(initial);
		
	par = init();

	if(argc > 1)
	{
		for(i = 1; i < argc; i++)
		{
			line = argv[i];
			if(line == "-t")
				par.th = atof(argv[i+1]);
			if(line == "-d")
				par.dimensions = atoi(argv[i+1]);
			if(line == "-b")
				par.beta = atof(argv[i+1]);
			if(line == "-d1")
			{
				par.d1.name = argv[i+1];
				par.d1.type = argv[i+2];
				par.d1.vigilance = atof(argv[i+3]);
			}
			if(line == "-d2")
			{
				par.d2.name = argv[i+1];
				par.d2.type = argv[i+2];
				par.d2.vigilance = atof(argv[i+3]);
			}
			if(line == "-d3")
			{
				par.d3.name = argv[i+1];
				par.d3.type = argv[i+2];
				par.d3.vigilance = atof(argv[i+3]);
			}
			if(line == "-d4")
			{
				par.d4.name = argv[i+1];
				par.d4.type = argv[i+2];
				par.d4.vigilance = atof(argv[i+3]);
			}

			if(line == "-i1")
				par.input1 = argv[i+1];
			if(line == "-i2")
				par.input2 = argv[i+1];
			if(line == "-o1")
				par.output1 = argv[i+1];
			if(line == "-o2")
				par.output2 = argv[i+1];
			if(line == "-o3")
				par.output3 = argv[i+1];
			if(line == "-rand")
				par.randomize = true;
			if(line == "-day")
				par.day = true;
			if(line == "-hour")
				par.hour = true;
			if(line == "-p2")
				par.phase2 = true;
			if(line == "-e")
				par.entropy = true;
			if(line == "-r")
				par.radius = atoi(argv[i+1]);
			if(line == "-h")
			{
				printHelp();
				return 0;
			}
		}
	}

	cout << "\n\nParameters are : " << "\n\tThreshold - " << par.th;
	cout << "\n\tVigilance - " << par.d1.vigilance << " " << par.d2.vigilance << " " << par.d3.vigilance;
	cout << "\n\tElliptical Radius - " << par.radius;
	cout << "\n\tInput File - " << par.input1;
	cout << "\n\tOutput Files - " << par.output1 << " " << par.output2 << " " << par.output3;

	file.open(par.input1.c_str());

	while(!file.eof())							//get input values from csv file
	{
		temp = new sample;
		getline(file,input,'\n');
		if((input.size()<1)||(input[0]=='#'))
		{
		continue;
		}
		first = last = 0;
		
		last = input.find(',',first);
		conversion = input.substr(first,last-first);
		temp->sip = conversion;
		first = last+1;

		last = input.find(',',first);
		conversion = input.substr(first,last-first);
		temp->dip = conversion;
		first = last+1;

		last = input.find(',',first);
		conversion = input.substr(first,last-first);
		cstr = new char [conversion.size()+1];
		strcpy(cstr, conversion.c_str());
		temp->bytes = atoi(cstr);
		first = last+1;

		last = input.find(',',first);
		conversion = input.substr(first,last-first);
		cstr = new char [conversion.size()+1];
		strcpy(cstr, conversion.c_str());
		temp->startTime = atoi(cstr);
		first = last+1;

		last = input.find(',',first);
		conversion = input.substr(first,last-first);
		cstr = new char [conversion.size()+1];
		strcpy(cstr, conversion.c_str());
		temp->endTime = atoi(cstr);
		first = last+1;

		temp->deltaTime = temp->endTime - temp->startTime;

		inputdata.push_back(*temp);
		count++;

		delete temp;
	}

	if(par.randomize)
		randomize(inputdata);
	
	numSamples = count;
	ns = numSamples;
	cout << "\n\nInput " << count << " samples";
	file.close();

	for(i = 0; i < inputdata.size(); i++)			//calculate IP distance for all inputs
	{
		inputdata[i].ipDistance = ipDistance(inputdata[i].sip, inputdata[i].dip);
	}

	normalizeTime(inputdata);

	high = findHigh(inputdata);				//find high and low values for all inputs to determine range
	low = findLow(inputdata);

	range[0] = high.ipDistance - low.ipDistance;
	range[1] = high.bytes - low.bytes;
	range[2] = high.deltaTime - low.deltaTime;

	cout << "\n\nDimension 1 Range : " << range[0] << "\nDimension 2 Range : " << range[1] << "\nDimension 3 Range : " << range[2];
	
	analyze(inputdata, cluster, par.beta, par.d1.vigilance, par.d2.vigilance, par.d3.vigilance, par.d4.vigilance, colormap, par.dimensions, par.radius, range);						//initial assignment of samples to cluster;

	count = 1;
	initClusters = cluster.size();

	cout << "\n\nInitial cluster assignments complete, re-evaluating for fluctuations\n";

	do{
		fluctuations = fluctuate(inputdata, cluster, par.beta, par.d1.vigilance, par.d2.vigilance, par.d3.vigilance, par.d4.vigilance, count, colormap, par.dimensions, par.radius, range);				//iterate through all clusters and look for a better match;
	flux.push_back(fluctuations);
	cout << "\nIteration # " << count << "\tFluctuations : " << fluctuations;
	count++;
	}while (fluctuations > 1);

	fluxClusters = cluster.size();
	iterations = count;

	count = 0;
	
	
	idAnomolies(cluster, par.th, inputdata, par.output2);			//identifies potentially anomolous traffic and outputs all related data
	//printCluster(cluster);							//Display clusters on screen

	outputClusterData(cluster, par.output1, inputdata);							//Outputs final clusters to file
//	outputTimeData(inputdata, cluster, par.input1, numSamples, colormap, iterations, initClusters, fluxClusters, iterations2, numSamples2);
	outputCoords(inputdata, cluster, par.output3, par.dimensions);		//output dimension data to file for GNU plot
	outputAnomalyTimeGraph(cluster, inputdata);

	return 0;
}
