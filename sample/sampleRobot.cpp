#include <iostream>
#include "rsdgMission.h"
#include <vector>
#include <stdlib.h>
#include <unistd.h>

using namespace std;

bool coke;
bool pepsi;
int cokePref;
int pepsiPref;
int budget;

string inputFile;
string outputFile;

rsdgMission* setupRSDG();
rsdgPara* paraCoke;
rsdgPara* paraPepsi;
void* f1 (void*);
void* f2 (void*);
rsdgMission* rsdg;

//robot
void* robot(void*);

int main(int argc, char* argv[]){
	if(argc<2){
		cokePref=1;
		pepsiPref=1;
	}else{
		for(int i = 1; i<argc; i++){
			string arg = argv[i];
			if(arg=="-coke"){
				cokePref=atoi(argv[++i]);
			}
			if(arg=="-pepsi"){
				pepsiPref=atoi(argv[++i]);
			}
			if(arg=="-xml"){
				inputFile = argv[++i];			
			}
			if(arg=="-b"){
				budget = atoi(argv[++i]);
			}
		}
	}
	outputFile = "./problem.lp";
	rsdg = setupRSDG();
	rsdg -> start();
	//faking robot
	pthread_t fakerobot;
	pthread_create(&fakerobot,NULL,&robot,NULL);
	sleep(5);
	pthread_cancel(fakerobot);
	sleep(15);
	rsdg -> stopSolver();
	rsdg -> cancel();
	return 1;;
}
//fake robot
/*
read the flags to generate command to robot
sleep(2): assuming after 2 seconds the robot came back from the first target
setBudget(): it should set the budget to current budget, i.e. 30(could be any number, depends on the inital budget and the cost in the first pick)
udpateWeight: update the weight of the balls that have been picked up, here I assumes it picked up Pepsi
	      so it updates the weight for 'pickPepsi' and 'pepsiCan' to 0. 
	      by doing the updateWeight, it will enable the solver to keep selecting 'pickPeipsi'.

Your robot should know that even the flag for pepsi is still true in the second solver consulting, you don't have to pick it up again. So you should have a logic of determing which can have I already picked up.

The reason of doing so:
We want to keep the solution consistent through out the entire mission. If it chooses 'pickPepsi' at the begining, it will always choose this if nothing goes wrong. The correct interpretion of 'pickPepsi' is 'getting the user a pepsi at the end'

thanks

example call-line:
./test -xml sample.xml -coke 10 -pepsi 20 -b 60
*/
void* robot (void* arg){
	while(1){
		pthread_testcancel();
		if(coke && pepsi) cout<<"picking up both"<<endl;
		else if(!coke && !pepsi) cout<<"not picking anything"<<endl;
		else {string bla= coke?"picking up coke":"picking up pepsi";
			cout<<bla<<endl;
		}
		sleep(2);
		rsdg->setBudget(30);
		rsdg->updateWeight("pickPepsi",0);
		rsdg->updateWeight("pepsiCan",0);
		rsdg->printProb("problem.lp");
		rsdg->reconfig();
	}
	return NULL;
}



//init RSDG
rsdgMission* setupRSDG(){
	paraCoke = new rsdgPara();//parameter for coke
	paraPepsi = new rsdgPara();//parameter for pepsi
	rsdgMission* res = new rsdgMission();
	res->regService("COKE","pickCoke",&f1,make_pair(paraCoke,1));
	res->regService("PEPSI","pickPepsi",&f2,make_pair(paraPepsi,1));
	res->regService("COKE","dropCoke",&f1,make_pair(paraCoke,0));
	res->regService("PEPSI","dropPepsi",&f2,make_pair(paraPepsi,0));
	/**************select local solver*************/
	res->setSolver(LPSOLVE);
	/***********/
	res->generateProb(inputFile);
	res->setBudget(budget);
	res->updateMV("PEPSI",pepsiPref,false);
	res->updateMV("COKE",cokePref,false);
	res->printProb(outputFile);//for validating
	res->setupSolverFreq(0);//reconfig manually
	return res;
}

//run functions for nodes
void* f1 (void* arg){
	int para = paraCoke->intPara;
	coke = para==1?true:false;
	return NULL;
}

void* f2 (void* arg){
	int para = paraPepsi->intPara;
	pepsi = para==1?true:false;
	return NULL;
}
