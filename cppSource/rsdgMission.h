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

// Class for parameter holder
class rsdgPara{
        public:
                int intPara;
};

// Class for work unit
class rsdgUnit{
        int unit;
        public:
                void set(int u);
                int get();
};

// Class for a rsdg Service (service >> layer >> node)
class rsdgService
{
        string name; // name of the service
        /**
         * for synchronization of data flow dependency
         */
        bool READY;
        int bufferReady;
        void* buffer;

        bool DEBUG = false;
        rsdgUnit* unit; // the total work unit
        rsdgPara* para; // the rsdgPara associated to this service
        vector<rsdgService*> parents; // for dependency checks, all parents of this service in RSDG. parent: ancestors
        pthread_t sThread; // the thread managing this service
        bool single; // set to true if the service only manages 1 runnable
        vector<string> node_lists; // a list of nodes in this service
        string curNode;

        public:
        // Constructor(s)
        rsdgService();
        rsdgService(string);
        // Return the name
        string getName();
        // Set the total work unit
        void setUnit(int m);
        // Return the finished unit
        int getUnit();
        // Return the thread
        pthread_t getThread();
        // Buffer setter(s)
        void setBufferReady(){bufferReady = 1;}
        void setBufferUsed(){bufferReady = 0;}
        void setBufferHold(){bufferReady = -1;}
        // Status setter
        void setStatus(bool b){READY = b;}
        // Status getter
        int getBufferStatus(){return READY;}
        // Return the parents
        vector<rsdgService*> getParents();
        // Buffer getter
        void* get(pthread_t t);
        // Buffer setter
        void set(pthread_t t, void* obj);
        // Run the runnable associated with the selected node
        void run(string node, void*f(void*));
        // Update the selected node (and activate the new node)
        void updateNode(void*(*)(void*),string);
        // Add a node to the service
		void addNode(string node_name);
        // Set the single indicator
        void setSingle(bool single);
        // Return the single indicator
        bool isSingle();
        // Return the node lists
        vector<string>& getList();
        // Set the curnode
        void setCurNode(string node);
        void setDebug();
        // Logger for service
		void logWarning(string msg);
		void logDebug(string msg);
		void logInfo(string msg);
};

class rsdgMission{
	public: const static bool LP_SOLVE = true;
	public: const static bool GUROBI = false;
	public: const static bool LOCAL = true;
	public: const static bool REMOTE = false;
	bool DEBUG = false; // set to true if debug info is needed
	int numThreads;
	const string pythonScript = "/home/ubuntu/parsec-3.0/rsdglib/modelConstr/parseData.py";
	double predictedCost = 0.0;
	double realCost = 0.0;

	// FACT file for cost
	ofstream fact;
	// Observed FACT file
	ofstream RS_fact;

	map<string, int> runnableID;
	map<string, int> threadID;
	map<string, string> basicToService;
	map<string, rsdgService*> serviceMap;
	map<string, pair<rsdgPara*, int> > paraList;
	map<string, rsdgPara*> contParaList;
	map<string, vector<string> > depChain;//kto a service's dependence
	map<string, int> threadPref;
	map<string, string> selected;
	map<string, double> offlineCost;
	map<string, double> offlineMV;
	map<string, double> contServiceValue;
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
	bool CONT = false;
	ofstream logfile;

	//mission related;
	RSDG* graph;
	string outfileName;
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
	bool offline_search = false;
	bool LOGGER = false;
	bool update = false;
	long freq;
	
	//result
	double maxMV;
	double minEnergy;
	bool solvable=true;

	//thread+runnable list
	vector<void*(*)(void*)> runnableList;
	vector<rsdgService*> serviceList;

	void genAllConfigs(int, vector<string>);
	public:		
		rsdgMission();
		rsdgService* getService(string name);
		void regService(string, string, void*(*)(void*), bool, pair<rsdgPara*, int> );
		void regService(string, string, void*(*)(void*),bool);
		void regContService(string, string, void*(*)(void*), rsdgPara*);
		void setupSolverFreq(int);
		void setUnit(int);
		void consultServer();
		void updateSelection(vector<string>& result);
		void applyResult();
		void updateThread(rsdgService* s,string basicNode, double value);
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
				it->second->setCurNode("");
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
		void readContTrainingSet();
		void setDebug();
		void logWarning(string msg);
		void logDebug(string msg);
		void logInfo(string msg);
		double getFreq();
};
#endif
