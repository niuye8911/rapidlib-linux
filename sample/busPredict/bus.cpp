#include<iostream>
#include<fstream>
#include<sstream>
#include "busTime.h"
#include<stdio.h>
#include<stdlib.h>
#include<unistd.h>
#include<time.h>

using namespace std;

ifstream busData;



void readABus(int id){
	Bus b;
	b.setId(id);
	int curID;
	string plateID;
	double longtitude;
	double lagtitude;
	double speed;
	string line;

	while(getline(busData,line)){
		Time time;
		istringstream linestream(line);
		string element;
		getline(linestream,element,',');
		curID = stoi(element);
		if(curID!=id)continue;
		cout<<"found"<<endl;
		getline(linestream,element,':');
		time.h = stoi(element);
		getline(linestream,element,':');
		time.m = stoi(element);
		getline(linestream,element,',');
		time.s = stoi(element);
		getline(linestream,element,',');
		plateID = element;
		getline(linestream,element,',');
		longtitude = stof(element);
		getline(linestream,element,',');
		lagtitude = stof(element);
		getline(linestream,element,',');
		speed = stof(element);
			//setup the bus obj
		b.setPlate(plateID);
		b.addTime(time);
		cout<<time.h<<":"<<time.m<<":"<<time.s<<endl;
	}	
	cout<<"done"<<endl;
	b.sortT();
	b.reportStat();
}

int main(int argc, char * argv[]){
	//parse the argument
	string filename(argv[1]);
	busData.open(filename);
	readABus(65293);
	busData.close();
	return 1;
}
