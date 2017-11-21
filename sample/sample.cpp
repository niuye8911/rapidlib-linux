#include "rsdgMission.h"
#include <iostream>
#include <unistd.h>
#include <queue>
#include <sys/time.h>
#include <stdlib.h>

using namespace std;

rsdgMission* testMission;
rsdgPara* paraCPU;
rsdgPara* paraApr;
queue<timeval> jobqueue;

void* f1(void* arg){
	int para = paraCPU->intPara;
	if(para==1)
		system( "./energy/setlowpwr.sh" ); 
	else if(para==2){
		system( "./energy/setcpu.sh 0 1") ;
		system( "./energy/setcpu.sh 1 1") ;
		system( "./energy/setcpu.sh 2 0") ;
		system( "./energy/setcpu.sh 3 0") ;
	}
	else if(para==3){
		system( "./energy/setcpu.sh 0 1") ;
                system( "./energy/setcpu.sh 1 1") ;
                system( "./energy/setcpu.sh 2 1") ;
                system( "./energy/setcpu.sh 3 0") ;
	}
	else{
		system( "./setmaxpwr.sh") ;
	}
}

void core(timeval reqStart){
	timeval procT;
	gettimeofday(&procT,0);
	vector<double> test;
	int i = 0;
	test.push_back(2);
	for(;i<1000;i++){
		test[0]=test[0]/2.0;
	}
	timeval endT;
	gettimeofday(&endT,0);
	double elaps = (endT.tv_sec - reqStart.tv_sec)*1000000 + (endT.tv_usec-reqStart.tv_usec);
	elaps /= 1000;
	cout<<reqStart.tv_sec<<":"<<reqStart.tv_usec<<" ";
	cout<<procT.tv_sec<<":"<<procT.tv_usec<<" ";
	cout<<endT.tv_sec;
	cout<<":"<<endT.tv_usec;
	cout<<" elapsed:"<<elaps<<endl;
}

void*job(void* arg){
	timeval sT;
	gettimeofday(&sT,0);
	jobqueue.push(sT);
	return NULL;
}

void * exec(void* arg){
	timeval *tv = (timeval*)arg;
	core(*tv);
}
void* executor(void* arg){
	while(true){
		int jobleft = jobqueue.size();
		testMission->setUnit(jobleft);
		testMission->reconfig();
		for(int i = 0;i<jobleft; i++){
			timeval cur = jobqueue.front();
			jobqueue.pop();
			pthread_t newT;
			core(cur);
		}
		usleep(1000000);
	}	

}


void* jobCreater(void* arg){
	vector<pthread_t> joblist;
	joblist.resize(10000);
	int i = 0;
	for(i=0; i<100; i++){
		//pthread_create(&joblist[i],NULL,job,NULL);
		timeval sT;	
		gettimeofday(&sT,0);
		jobqueue.push(sT);
		usleep(50000);
	}
	timeval curT;
	gettimeofday(&curT,0);
	cout<<"dispathching.................."<<curT.tv_sec<<endl;
	for(i=100; i<1100; i++){
		//pthread_create(&joblist[i],NULL,job,NULL);
		timeval sT;
                gettimeofday(&sT,0);
                jobqueue.push(sT);
                usleep(50000);
	}
	sleep(5);
	gettimeofday(&curT,0);
	cout<<"dispathching.................."<<curT.tv_sec<<endl;
	for(i=1100; i<3000; i++){
                pthread_create(&joblist[i],NULL,job,NULL);
        }
	sleep(5); 
	gettimeofday(&curT,0);
	cout<<"dispathching.................."<<curT.tv_sec<<endl;
	for(i=3000; i<4000; i++){
                pthread_create(&joblist[i],NULL,job,NULL);
                usleep(500000);
        }
}

int main(){
	//start the RSDG
	testMission = new rsdgMission();
	paraCPU = new rsdgPara();
	paraApr = new rsdgPara();
	pair<rsdgPara*,int> testParaPair = make_pair(paraCPU,1);
	testMission->regService("screen","100p",&f1, false,testParaPair);	
	testMission->regService("screen","80p",&f1, false,make_pair(paraCPU,2));
	testMission->regService("screen","50p",&f1, false,make_pair(paraCPU,3));
	testMission->regService("screen","20p",&f1, false,make_pair(paraCPU,4));
	testMission->regService("screen","10p",&f1, false,make_pair(paraCPU,5));	

		testMission->regService("quality","720p",&f1, false,testParaPair);	
	testMission->regService("quality","480p",&f1, false,make_pair(paraCPU,2));
	testMission->regService("quality","360p",&f1, false,make_pair(paraCPU,3));
	testMission->regService("quality","240p",&f1, false,make_pair(paraCPU,4));
	testMission->regService("quality","144p",&f1, false,make_pair(paraCPU,5));	
	/*
	testMission->updateMV("screen",5);
	testMission->updateMV("quality",5);	
	testMission->setBudget(10000000);
	//start the executor
	pthread_t exeC;
	pthread_create(&exeC, NULL, executor, NULL);
	//initiate the job creater
	pthread_t jobC;
        pthread_create(&jobC, NULL, jobCreater, NULL);
	pthread_join(jobC,NULL);
	pthread_join(exeC,NULL);
	*/
	string infile = "rsdginst.xml";
	string outfile = "output.lp";
	testMission->generateProb(infile);

	testMission->updateMV("screen",25,false);
	testMission->updateMV("quality",5,false);
	testMission->setBudget(9999999);
	
	testMission->addConstraint("sys",true);
	testMission->addConstraint("comm",true);
	testMission->addConstraint("screen",true);
	testMission->addConstraint("quality",true);
		testMission->printProb(outfile);

testMission->genProductProfile();
	//testMission->printProb(outfile);
	return 1;
}
