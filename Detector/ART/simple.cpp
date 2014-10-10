#include <iostream>
#include <fstream>
#include <stdio.h>
#include <stdlib.h>
#include <string>
#include <iomanip>

using namespace std;

bool isIP(string temp)
{
	int count = 0;
	int i = 0;

	for(i = 0; i < temp.length(); i++)
	{
		if(temp[i] == '.')
			count++;
	}

	if(count == 3)
		return true;
	else
		return false;
}

string extract(string temp)
{
	int i = 0;
	int location = 0;
	string num;
	num[0] = temp[3];

	for(i = 0; i < temp.length(); i++)
	{
		if(temp[i] == '.')
			location = i;
	}
	
	location = location - 12;
	if(location > 0)
	{
		for(i = 0; i < location; i++)
			num[i+1] = temp[4+i];
	}

	return num;
}

void ARO(string input, string output)
{
	ifstream in;
	ofstream out;
	char * file;
	string source;
	string destination;
	string size1, size2;
	string duration = "00";
	string year, month, day, hour, min, sec;
	string temp;
	bool ipflag = true;
	int first, last;


	in.open(input.c_str());
	out.open(output.c_str());

	while(!in.eof())
	{
		file = new char[20];
		in >> file;

		if(file[0] == 'T' && file[1] == 'C' && file[2] == 'P')
			continue;
		if(file[0] == 'U' && file[1] == 'D' && file[2] == 'P')
			continue;
		if(file[8] == '.' && file[11] == ':' && file[14] == ':')
		{
			temp = file;
			year = temp.substr(0,4);
			month = temp.substr(4,2);
			day = temp.substr(6,2);
			hour = temp.substr(9,2);
			min = temp.substr(12,2);
			sec = temp.substr(15,2);
			continue;
		}
		
		if(file[0] == '[' && file[9] == ']')
		{
			duration[0] = file[7];
			duration[1] = file[8];
			continue;
		}
		
		if(isIP(file))
		{
			if(ipflag)
			{
				source = file;
				ipflag = false;
			}

			else if(!ipflag)
			{
				destination = file;
				ipflag = true;
			}
			continue;
		}
		if(file[0] == 'p')
			continue;
		if(file[0] == '<')
			continue;
		if(file[0] == '*')
			continue;
		if(file[0] == 'p')
			continue;
		if(file[0] == 'C' && file[1] == 'b')
		{
			size1 = file;
			last = size1.find(',');
			size1 = size1.substr(3,last - 3);
			continue;
		}
		if(file[0] == 'C' && file[1] == 'p')
			continue;
		if(file[0] == 'S' && file[1] == 'b')
		{
			size2 = file;
			last = size2.find(',');
			size2 = size2.substr(3,last - 3);
			continue;
		}
		if(file[0] == 'S' && file[1] == 'p')
		{
			out << source << "," << destination << "," << size1 << "," << size2 << "," << duration << "," << year << "," << month << "," << day << "," << hour << "," << min << "," << sec << endl;
			duration = "00";
			continue;
		}
		delete file;
	}

	out.close();
	in.close();
}

void FS(string input, string output)
{
	ifstream in;
	ofstream out;
	string file;
	string source;
	string destination;
	double start;
	double end;
	double duration;
	string size;
	int first, last;
	int counter = 0;


	in.open(input.c_str());
	out.open(output.c_str());

	while(!in.eof())
	{
		counter++;
		in >> file;

		if(file == "textexport")
			continue;
		if(counter == 2 || counter == 3)
			continue;
		if(counter == 4)
		{
			start = atof(file.c_str());
			continue;
		}
		
		if(counter == 5)
		{
			end = atof(file.c_str());
			continue;
		}
		
		if(counter == 6)
		{
			first = file.find(':');
			source = file.substr(0,first);
			first = file.find('>');
			last = file.rfind(':');
			destination = file.substr(first + 1, last - first - 1);
			continue;
		}

		if(counter == 7 || counter == 8 || counter == 9 || counter == 10)
		{
			continue;
		}

		if(counter == 11)
		{
			size = file;
			continue;
		}
		if(counter == 12)
		{
			counter = 0;
			duration = end - start;
			out << source << "," << destination << "," << size << "," << setprecision (16) << start << "," << setprecision (16) << end << endl;
			duration = 0.0;
		}
	}

	out.close();
	in.close();
}

int main(int argc, char *argv[])
{
	string line;
	string input, output;
	bool aro, fs;
	int i = 0;

	input = "input.txt";
	output = "output.txt";

	aro = false;
	fs = false;

	if(argc > 1)
	{
		for(i = 1; i < argc; i++)
		{
			line = argv[i];
			if(line == "-i")
				input = argv[i+1];
			if(line == "-o")
				output = argv[i+1];
			if(line == "-aro")
				aro = true;
			if(line == "-fs")
				fs = true;
		}
	}

	if(aro)
		ARO(input, output);

	if(fs)
		FS(input, output);

	
	return 0;
}