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

void outputAnomoly(clusters c, vector<sample> &input, string name)
{
	ofstream file;
	int i;
	int end;
	int id;
	int count = 0;

	end = c.members.size();

	file.open(name.c_str(), ios::app);
	file << "\n\nCluster Number - " << c.id;
	file << "\n\tPrototype Bytes - " << c.proto.bytes << "\tPrototpye IP Distance - " << c.proto.ipDistance;
	file << "\n\nCluster Members :\n";

	for(i = 0; i < end; i++)
	{
		id = c.members[i];
		file << "Sample # " << id << "\tSource IP - " << input[id].sip << "\tDestination IP - " << input[id].dip << "\tBytes - " << input[id].bytes << "\tDuration - " << input[id].deltaTime << endl;
		count++;
	}
	file << "\n\nTotal anamalous flows = " << count;
	file.close();
}

void outputClusterData(vector<clusters> &cluster, string filename, vector<sample> &input)	//prints all cluster data in a single file
{

	ofstream file;
	int i = 0;
	int j = 0;

	file.open(filename.c_str());

	for (i = 0; i < cluster.size(); i++)
	{
		file << "Cluster # " << i+1 << endl;
		file << "\nPrototype Vector - \tBytes : " << cluster[i].proto.bytes << "\t IP Distance : " << cluster[i].proto.ipDistance;
		file << "\t Flow Duration : " << cluster[i].proto.deltaTime << endl;
		for (j = 0; j < cluster[i].members.size(); j++)
		{
			file << "\n\t Member " << cluster[i].members[j] << endl;
			file << "\t\t Bytes : " << input[cluster[i].members[j]].bytes << "\t IP Distance : " << input[cluster[i].members[j]].ipDistance;
			file << "\t Flow Duration : " << input[cluster[i].members[j]].deltaTime;
		}
		file << "\n\n";
	}

	file.close();
}

void outputCoords(vector<sample> &input, vector<clusters> &cluster, string filename, int d)	//outputs coordinate data for graphing with GNU plot
{
	ofstream file;
	int i = 0;
	int j = 0;
	int point;
	int pos;

	file.open(filename.c_str());

	for(i=0; i < cluster.size(); i++)
	{
		for(j = 0; j < cluster[i].members.size(); j++)
		{
			point = cluster[i].members[j];
			file << input[point].bytes << "\t" << input[point].ipDistance << "\t" << input[point].deltaTime << "\t" << input[point].clusterAssigned << endl;
		}
	}

	file.close();

/*	pos = filename.rfind('.');
	filename.erase(pos-1);
	filename.insert(pos-1, "2.txt");
	file.open(filename);
	
	for(i=0; i < cluster.size(); i++)
	{
		for(j = 0; j < cluster[i].members.size(); j++)
		{
			point = cluster[i].members[j];
			file << input[point].ipDistance << "," << input[point].clusterAssigned << endl;
		}
	}

	file.close();

	pos = filename.rfind('.');
	filename.erase(pos-1);
	filename.insert(pos-1, "3.txt");
	file.open(filename);
	
	for(i=0; i < cluster.size(); i++)
	{
		for(j = 0; j < cluster[i].members.size(); j++)
		{
			point = cluster[i].members[j];
			file << input[point].deltaTime << "," << input[point].clusterAssigned << endl;
		}
	}

	file.close(); */
}

void printCluster(vector<clusters> &cluster)		//outputs all clusters to screen
{
	int i = 0;
	int j = 0;
	cout << "\n\n";
	for (i=0; i < cluster.size(); i++)
	{
		cout << "Cluster #" << i+1 << endl;
		cout << "     Members: ";
		for (j=0; j < cluster[i].members.size(); j++)
		{
			cout << cluster[i].members[j] << ",";
		}
		cout << "\n          Cluster Averages:      bytes - " << cluster[i].proto.bytes << "     IP Distance - " << cluster[i].proto.ipDistance << endl;
	}
	cout << "\n\n";
}

void outputClusters(vector <clusters> & cluster, vector<sample> &input)		//output cluster data to file
{
	ofstream file;
	string filename = "c://data//clusterSummary.txt";
	int i = 0;

	file.open(filename.c_str());
	file << "Nominal clusters : \n\n";

	for(i = 0; i < cluster.size(); i++)
	{
		if(!cluster[i].anom)
			file << "Cluster - " << cluster[i].id << "\tIP Distance - " << cluster[i].proto.ipDistance << "\tBytes - " << cluster[i].proto.bytes << "\tDuration - " << cluster[i].proto.deltaTime;
	}

	file << "Anomolous clusters : \n\n";

	for(i = 0; i < cluster.size(); i++)
	{
		if(cluster[i].anom)
			file << "Cluster - " << cluster[i].id << "\tIP Distance - " << cluster[i].proto.ipDistance << "\tBytes - " << cluster[i].proto.bytes << "\tDuration - " << cluster[i].proto.deltaTime;
	}
	file.close();
}

void outputAnomalyTimeGraph(vector <clusters> & cluster, vector<sample> &input)		//outputs data for graphing anomly occurences over time
{
	ofstream file;
	string filename = "anomalyTimeData.txt";
	int i, j = 0;
	int id;

	file.open(filename.c_str());

	for(i = 0; i < cluster.size(); i++)
	{
		if(cluster[i].anom)
		{
			for(j = 0; j < cluster[i].members.size(); j++)
			{
				id = cluster[i].members[j];
				file << input[id].startTime << "\t1" << endl;
			}
		}
	}
	file.close();
}
