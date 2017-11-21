#ifndef RSDGMISSION_H 
#define RSDGMISSION_H
#include <map>

#include <string>
#include <iostream>
#include <fstream>
#include <fstream>
#include <vector>
#include <utility>
#include "RSDG.h"

using namespace std;

extern bool verboseRSDG;

void* startSolver(void*);

long long getCurrentTimeInMilli();

extern string RSDG_TAG;

class rsdgPara{
        public:
                int intPara;
};

class rsdgUnit{
        int unit;
        public:
                void set(int u);
                int get();
};

class rsdgService
{
        std::string name;
        bool READY;
        int bufferReady;
        rsdgUnit* unit;
        rsdgPara* para;
        std::vector<rsdgService*> parents;
        pthread_t sThread;

        public:
		bool single;
                void* buffer;
		vector<string> node_lists;
		int cur_selected_id = 0;
                std::string curNode;
                rsdgService();
                std::string getName();
                void setUnit(int m);
                int getUnit();
                pthread_t getThread();
                void setBufferReady(){bufferReady = 1;}
                void setBufferUsed(){bufferReady = 0;}
                void setBufferHold(){bufferReady = -1;}
                void setStatus(bool b){READY = b;}
                int getBufferStatus(){return READY;}
                std::vector<rsdgService*> getParents();
                void* get(pthread_t t);
                void set(pthread_t t, void* obj);
                void run(std::string node, void*f(void*));
                void updateNode(void*(*)(void*),std::string);
		void addNode(string node_name);
                rsdgService(std::string name);
};

class rsdgMission{
	public: const static bool LP_SOLVE = true;
	public: const static bool GUROBI = false;
	public: const static bool LOCAL = true;
	public: const static bool REMOTE = false;
	//public: const static string RSDG_TAG = "//RSDG DEBUG INFO:";
	int numThreads;
	string pythonScript = "/home/ubuntu/parsec-3.0/rsdglib/modelConstr/parseData.py";
	double  predictedCost = 0.0;
	double realCost = 0.0;
	double THRESHOLD = 10;
	ofstream fact;
	ofstream RS_fact;
	map<string, int> runnableID;
	map<string, int> threadID;
	map<string, string> basicToService;
	map<string, rsdgService*> serviceMap;
	map<string, pair<rsdgPara*, int> > paraList;
	map<string, vector<string> > depChain;//kto a service's dependence
	map<string, int> threadPref;
	map<string, string> selected;
	map<string, double> offlineCost;
	map<string, double> offlineMV;
	vector<vector<string>> all_configs;
	int curTrainingId = -1;
	int curUpdatingId = -1;
	bool lpsolve;
	bool local;
	long long lastCheckPoint;
	long long timeSinceLastCheckPoint=0;
	long long startTime = -1;
	bool TRAINING_MODE = false;
	int unitBetweenCheckPoints = 0;
	ofstream logfile;

	//mission related;
	int budgetType;
	rsdgUnit unit;
	long budgetTracker;
	int budget;
	int curBudget;
	double objValue;
	pthread_t monitor;
	int num_of_reconfig = 0;
	int total_reconfig_time = 0;
	vector<vector<string>> RS;

	//result
	double maxMV;
	double minEnergy;

	//thread+runnable list
	vector<void*(*)(void*)> runnableList;
	vector<rsdgService*> serviceList;

	void genAllConfigs(int, vector<string>);
	public:
		bool solvable=true;
		bool update = false;
		bool offline_search = false;
		bool LOGGER = false;
		double totalTime;
		long freq;
		string outfileName;
		RSDG* graph;//made public so as to easily modify by user
		rsdgMission();
		rsdgService* getService(string name);
		void regService(string, string, void*(*)(void*), bool, pair<rsdgPara*, int> );
		void regService(string, string, void*(*)(void*),bool);
		void setupSolverFreq(int);
		void setUnit(int);
		void consultServer();
		void updateSelection(vector<string>& result);
		void applyResult();
		void updateThread(rsdgService* s,string basicNode);
		void start();
		void generateProb(string);
		void setBudget(int);
		void updateMV(string, int, bool);
		int getBudget();
		void updateWeight(string,double);
		void updateWeight(string, string, double);
		int getNumThreads();
		int printPref(string serviceName);
		void setSolver(bool,bool);
		void finish_one_unit();
		void reconfig();
		void printProb(string);
		void stopSolver();
		void cancel();
		virtual void updateBudget();
		vector<string> getDep(string);
		void reset(){
			selected.clear();
			for(auto it = serviceMap.begin(); it!=serviceMap.end(); it++){
				if(it->second!=NULL)
				it->second->curNode=="";
			}
		}
		void addConstraint(string, bool);
		void addConstraint(string,string,bool);
		vector<string> localSolve();
		void setOutput(string);
		void getRes(vector<string>&, string);
		double genProductProfile();
		double getObj();
		void checkPoint();
		void updateModel(int);// this function will be called everytime before reconfig
		void setUnitBetweenCheckpoints(int);
		void printToLog();
		void setTraining();
		void genFact();
		void reconfig_training();
		void reconfig_updating();
		bool validate(vector<string>&);
		void filterConfigs();
		bool isFailed();
		void readRS(string);
		void updateRSDG();
		void setUpdate(bool);
		void resetTimer();
		void setLogger();
		void readMVProfile();
		void readCostProfile();
		vector<string> searchProfile();
		void setOfflineSearch();
};
#endif
