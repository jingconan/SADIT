#ifndef ART
#define ART
#include <string>

using namespace std;

struct date
{
	int year;
	int month;
	int day;
	int hour;
	int min;
	int sec;
};

struct sample
{
	string sip;					//source ip address
	int freq;					//frequency this source ip address occurs in all flows
	string dip;					//destination ip address
	double bytes;				//# of bytes in the flow (Outbound)
	double bytes2;				//# of bytes in the flow (Inbound)
	double packets;				//# of packets in the flow
	double ipDistance;			//calculated distance between source and destination ip
	float lat;				
	float lng;
	int clusterAssigned;		//cluster id the sample is currently assigned to
	double startTime;
	double endTime;
	double deltaTime;			//difference between start and finish times
	date time;
};

struct clusters
{
	int id;						//the id number of the cluster
	sample proto;				//represents the average value of all samples in the cluster
	vector<int> members;		//int is the index of the member in the input data array that belongs to this cluster
	vector<int> timeData;
	bool anom;					//identifies anomalous clusters
	bool newCluster;			//identifies clusters created after the learning process
};

struct dim
{
	string name;
	string type;
	float vigilance;
};

struct parameters
{
	float beta;				//beta parameter
	dim d1;
	dim d2;
	dim d3;
	dim d4;
	float th;				//detection threshold
	string input1;			//initial input
	string input2;			//second input if used
	bool phase2;			//second input used?
	bool hour;				//do temporal hour analysis?
	bool day;				//do temporal day analysis?
	bool randomize;			//randomize input data?
	bool entropy;			//do entropy analysis?
	int dimensions;				//number of dimensions
	string output1;			//clustering results
	string output2;			//anomolies
	string output3;			//graph coordinates
	int radius;				//max cluster elliptical size
};

parameters init()		//populate default values
{
	parameters par;

	par.beta = 0.5;
	par.input1 = "input1.txt";
	par.input2 = "0";
	par.d1.vigilance = 0.85;						//IP Distance
	par.d2.vigilance = 0.85;						//Flow Size (Outbound)
	par.d3.vigilance = 0.85;						//Flow Duration
	par.d4.vigilance = 0.85;						//Flow Size (Inbound)
	par.th = 0.2;
	par.dimensions = 3;
	par.hour = false;
	par.day = false;
	par.randomize = false;
	par.phase2 = false;
	par.entropy = false;
	par.output1 = "clusters.txt";
	par.output2 = "anomolies.txt";
	par.output3 = "coords.txt";
	par.radius = 1;

	return par;
}

#endif