#include<iostream>
#include"rsdgMission.h"

int main(){
	rsdgMission* testMission = new rsdgMission();
	testMission->generateProb("swaption.xml");
	testMission->setBudget(50);
	testMission->addConstraint("num", true);
	testMission->printProb("");
	testMission->setSolver(false,true);
	//testMission->consultServer();
	return 1;
}
